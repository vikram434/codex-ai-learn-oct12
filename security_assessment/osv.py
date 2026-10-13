"""Minimal OSV query client; absence of findings is not a security verdict."""

from dataclasses import asdict, dataclass
import json
import math
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


class OSVError(Exception):
    """Base class for source failures."""


class OSVTimeout(OSVError):
    """The source did not respond within the configured timeout."""


class OSVHTTPError(OSVError):
    def __init__(self, status: int):
        self.status = status
        super().__init__(f"OSV HTTP failure: {status}")


class OSVTransportError(OSVError):
    """Connection, DNS, or TLS failure."""


class OSVMalformedResponse(OSVError):
    """Response is not valid JSON with the expected OSV shape."""


@dataclass(frozen=True)
class Package:
    name: str
    ecosystem: str
    version: str

    def __post_init__(self):
        for field in ("name", "ecosystem", "version"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise ValueError(f"{field} must be a non-empty string without outer whitespace")


@dataclass(frozen=True)
class Vulnerability:
    id: str
    source_url: str


@dataclass(frozen=True)
class QueryResult:
    package: Package
    vulnerabilities: tuple[Vulnerability, ...]
    source: str

    @property
    def status(self) -> str:
        return "vulnerabilities_returned" if self.vulnerabilities else "no_vulnerabilities_returned"

    def to_dict(self) -> dict:
        result = asdict(self)
        result["status"] = self.status
        result["message"] = (
            "Vulnerabilities returned by this source."
            if self.vulnerabilities else
            "No vulnerabilities returned by this source; this is not proof that the package is secure."
        )
        return result


class OSVClient:
    def __init__(self, base_url: str = "https://api.osv.dev", timeout: float = 10):
        parts = urlsplit(base_url)
        if (parts.scheme not in ("http", "https") or not parts.hostname
                or parts.username or parts.password or parts.query or parts.fragment):
            raise ValueError("base_url must be an HTTP(S) URL without credentials, query, or fragment")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a positive finite number")
        self.query_url = base_url.rstrip("/") + "/v1/query"
        self.timeout = timeout

    def query(self, name: str, ecosystem: str, version: str) -> QueryResult:
        package = Package(name, ecosystem, version)
        payload = {"package": {"name": name, "ecosystem": ecosystem}, "version": version}
        request = Request(self.query_url, data=json.dumps(payload).encode("utf-8"),
                          headers={"Content-Type": "application/json", "Accept": "application/json"},
                          method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                if not 200 <= response.status < 300:
                    raise OSVHTTPError(response.status)
                raw = response.read()
        except HTTPError as exc:
            status = exc.code
            exc.close()
            raise OSVHTTPError(status) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise OSVTimeout("OSV query timed out") from exc
        except URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise OSVTimeout("OSV query timed out") from exc
            raise OSVTransportError(f"OSV transport failure: {exc.reason}") from exc
        except OSError as exc:
            raise OSVTransportError(f"OSV transport failure: {exc}") from exc
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise OSVMalformedResponse("OSV response is not valid JSON") from exc
        if not isinstance(data, dict):
            raise OSVMalformedResponse("OSV response must be an object")
        # OSV omits the vulns field for no matches and returns {}.
        if "vulns" not in data and data:
            raise OSVMalformedResponse("Unexpected response without vulns")
        entries = data.get("vulns", [])
        if not isinstance(entries, list):
            raise OSVMalformedResponse("vulns must be a list")
        findings = []
        seen = set()
        for entry in entries:
            identifier = entry.get("id") if isinstance(entry, dict) else None
            if (not isinstance(identifier, str) or not identifier.strip()
                    or any(char.isspace() or ord(char) < 32 for char in identifier)):
                raise OSVMalformedResponse("Each vulnerability must have a non-empty ID without whitespace")
            if identifier not in seen:
                seen.add(identifier)
                findings.append(Vulnerability(identifier, "https://osv.dev/vulnerability/" + quote(identifier, safe="")))
        return QueryResult(package, tuple(findings), self.query_url)

