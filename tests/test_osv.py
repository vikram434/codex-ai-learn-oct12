import io
from contextlib import redirect_stdout, redirect_stderr
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from security_assessment.osv import (
    OSVClient, OSVHTTPError, OSVMalformedResponse, OSVTimeout, OSVTransportError,
)
from security_assessment.__main__ import main

FIXTURES = Path(__file__).parent / "fixtures"


class OSVTests(unittest.TestCase):
    def test_recorded_assessment_cases_through_cli(self):
        cases = json.loads((FIXTURES / "assessment_cases.json").read_text())
        for case in cases:
            with self.subTest(case=case["case"]):
                stdout, stderr = io.StringIO(), io.StringIO()
                raw = (FIXTURES / case["response_fixture"]).read_bytes()
                with patch("sys.argv", ["assessment", "example", "PyPI", "1.0"]), \
                        patch("security_assessment.osv.urlopen", return_value=self.response(raw)), \
                        redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = main()
                output = json.loads(stderr.getvalue() if exit_code else stdout.getvalue())
                self.assertEqual(output["message"], case["expected_wording"])
                if case["case"] == "source_failure":
                    self.assertEqual(exit_code, 1)
                    self.assertEqual(output["error"], "OSVMalformedResponse")
                    self.assertEqual(output["status"], "source_failure")
                else:
                    self.assertEqual(exit_code, 0)
                    self.assertEqual(output["status"], case["expected_status"])

    def test_unavailable_cli_wording(self):
        for error in (OSVTimeout("timeout"), OSVHTTPError(503), OSVTransportError("unavailable")):
            with self.subTest(error=type(error).__name__):
                stderr = io.StringIO()
                with patch("sys.argv", ["assessment", "example", "PyPI", "1.0"]), \
                        patch("security_assessment.__main__.OSVClient.query", side_effect=error), \
                        redirect_stderr(stderr):
                    self.assertEqual(main(), 1)
                output = json.loads(stderr.getvalue())
                self.assertEqual(output["error"], type(error).__name__)
                self.assertEqual(output["message"], "Assessment unavailable from this source; no security conclusion can be drawn.")

    def response(self, raw, status=200):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = status
        response.read.return_value = raw
        return response

    def query_raw(self, raw):
        with patch("security_assessment.osv.urlopen", return_value=self.response(raw)):
            return OSVClient().query("example", "PyPI", "1.0")

    def test_request_and_validated_result(self):
        raw = (FIXTURES / "vulnerabilities.json").read_bytes()
        with patch("security_assessment.osv.urlopen", return_value=self.response(raw)) as send:
            result = OSVClient("http://localhost:9000/", timeout=2).query("example", "PyPI", "1.0")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:9000/v1/query")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), {
            "package": {"name": "example", "ecosystem": "PyPI"}, "version": "1.0"})
        self.assertEqual(send.call_args.kwargs, {"timeout": 2})
        self.assertEqual(result.to_dict()["package"], {"name": "example", "ecosystem": "PyPI", "version": "1.0"})
        self.assertEqual([v.id for v in result.vulnerabilities], ["GHSA-test-1234-5678", "CVE-2024-0001"])
        self.assertEqual(result.vulnerabilities[1].source_url, "https://osv.dev/vulnerability/CVE-2024-0001")
        self.assertEqual(result.status, "vulnerabilities_returned")

    def test_empty_is_not_secure(self):
        for filename in ("empty.json", "omitted.json"):
            with self.subTest(filename=filename):
                result = self.query_raw((FIXTURES / filename).read_bytes())
                self.assertEqual(result.vulnerabilities, ())
                self.assertEqual(result.status, "no_vulnerabilities_returned")
                self.assertIn("not proof", result.to_dict()["message"])

    def test_malformed_responses(self):
        cases = [b"not json", b"\xff", b"[]", b"null", b'{"error":"bad query"}',
                 b'{"vulns":null}', b'{"vulns":{}}', b'{"vulns":[null]}',
                 b'{"vulns":[{}]}', b'{"vulns":[{"id":""}]}',
                 b'{"vulns":[{"id":"bad id"}]}', (FIXTURES / "malformed.json").read_bytes()]
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(OSVMalformedResponse):
                self.query_raw(raw)

    def test_timeout(self):
        for error in (TimeoutError(), URLError(TimeoutError())):
            with self.subTest(error=error), patch("security_assessment.osv.urlopen", side_effect=error):
                with self.assertRaises(OSVTimeout):
                    OSVClient().query("example", "PyPI", "1.0")

    def test_http_failure(self):
        for status in (400, 429, 500):
            error = HTTPError("https://api.osv.dev/v1/query", status, "failure", {}, io.BytesIO(b"bad"))
            with self.subTest(status=status), patch("security_assessment.osv.urlopen", side_effect=error):
                with self.assertRaises(OSVHTTPError) as caught:
                    OSVClient().query("example", "PyPI", "1.0")
                self.assertEqual(caught.exception.status, status)

    def test_transport_failure(self):
        with patch("security_assessment.osv.urlopen", side_effect=URLError("DNS failure")):
            with self.assertRaises(OSVTransportError):
                OSVClient().query("example", "PyPI", "1.0")

    def test_invalid_inputs_never_send(self):
        with patch("security_assessment.osv.urlopen") as send:
            for args in (("", "PyPI", "1"), ("x", " ", "1"), ("x", "PyPI", None)):
                with self.subTest(args=args), self.assertRaises(ValueError):
                    OSVClient().query(*args)
            send.assert_not_called()
        for timeout in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                OSVClient(timeout=timeout)
        for url in ("file:///tmp/x", "https://user:pass@example.com", "https://example.com?q=x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                OSVClient(url)

    def test_ids_are_url_encoded(self):
        result = self.query_raw(b'{"vulns":[{"id":"a/b?c"}]}')
        self.assertEqual(result.vulnerabilities[0].source_url, "https://osv.dev/vulnerability/a%2Fb%3Fc")


if __name__ == "__main__":
    unittest.main()
