"""Bounded HTTP fetching with DNS pinning and redirect destination checks."""

import http.client
import ipaddress
import socket
import ssl
import threading
import zlib
from urllib.parse import urlparse, urljoin
from newspaper import Article as NewspaperArticle

MAX_BYTES = 8 * 1024 * 1024


def decode_body(data, content_encoding):
    """Bound both wire bytes and decompressed bytes; never unpack without a cap."""
    if len(data) > MAX_BYTES:
        raise ValueError("Source exceeds the 8 MB extraction limit.")
    encoding = content_encoding.strip().lower()
    if encoding in {"", "identity"}:
        return data
    if encoding not in {"gzip", "x-gzip", "deflate"}:
        raise ValueError("Source sent unsupported compressed content; supported encodings are gzip and deflate.")
    decoded = bytearray()
    remaining = data
    while remaining:
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS if encoding in {"gzip", "x-gzip"} else zlib.MAX_WBITS)
        try:
            decoded.extend(inflater.decompress(remaining, MAX_BYTES - len(decoded) + 1))
        except zlib.error:
            raise ValueError("Source sent invalid compressed content.") from None
        if len(decoded) > MAX_BYTES:
            raise ValueError("Decompressed source exceeds the 8 MB extraction limit.")
        if not inflater.eof:
            raise ValueError("Source sent truncated or invalid compressed content.")
        remaining = inflater.unused_data
        # Gzip permits concatenated members, with one cumulative output limit.
        if remaining and encoding == "deflate":
            raise ValueError("Source sent invalid trailing compressed content.")
    if not data:
        raise ValueError("Source sent empty compressed content.")
    return bytes(decoded)


def resolve_public(url):
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use a public HTTP or HTTPS URL without credentials.")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in {80, 443}:
        raise ValueError("Source URLs must use port 80 or 443.")
    addresses = socket.getaddrinfo(parsed.hostname, port, type=socket.SOCK_STREAM)
    ips = {entry[4][0] for entry in addresses}
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Internal-network source URLs are blocked.")
    return parsed, port, sorted(ips)[0]


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, address):
        super().__init__(host, port, timeout=20, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        sock = socket.create_connection((self.address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def fetch_html(url):
    for _ in range(6):
        parsed, port, address = resolve_public(url)
        connection = (
            PinnedHTTPS(parsed.hostname, port, address)
            if parsed.scheme == "https"
            else http.client.HTTPConnection(address, port, timeout=20)
        )
        try:
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            connection.request(
                "GET",
                path,
                headers={
                    "Host": parsed.netloc,
                    "User-Agent": "Mozilla/5.0 TRACE",
                    "Accept-Encoding": "gzip, deflate",
                },
            )
            active_socket = connection.sock
            timed_out = threading.Event()

            def abort():
                timed_out.set()
                try:
                    active_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

            timer = threading.Timer(20, abort)
            timer.daemon = True
            timer.start()
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("Source redirect has no destination.")
                url = urljoin(url, location)
                continue
            if response.status >= 400:
                raise ValueError(f"Source returned HTTP {response.status}.")
            data = response.read(MAX_BYTES + 1)
            data = decode_body(data, response.getheader("Content-Encoding", "identity"))
            if timed_out.is_set():
                raise ValueError("Source fetch exceeded its 20-second deadline.")
            content_type = response.getheader("Content-Type", "")
            encoding = (
                content_type.split("charset=")[-1].split(";")[0].strip()
                if "charset=" in content_type
                else "utf-8"
            )
            try:
                return data.decode(encoding, errors="replace")
            except LookupError:
                return data.decode("utf-8", errors="replace")
        finally:
            if "timer" in locals():
                timer.cancel()
            connection.close()
    raise ValueError("Too many source redirects.")


class SafeArticle(NewspaperArticle):
    def download(self, input_html=None, **kwargs):
        return super().download(
            input_html=fetch_html(self.url) if input_html is None else input_html,
            **kwargs,
        )
