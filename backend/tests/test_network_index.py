from pathlib import Path
import socket
from unittest.mock import Mock
import pytest
from workflows import network
from backend.engine import save_index, load_index


@pytest.mark.parametrize("encoding", ["gzip", "deflate"])
def test_http_compression_decodes_with_same_output_limit(encoding):
    import gzip
    import zlib
    source = "<html><body>Complete source evidence.</body></html>".encode()
    encoded = gzip.compress(source) if encoding == "gzip" else zlib.compress(source)
    assert network.decode_body(encoded, encoding) == source


def test_gzip_concatenated_members_keep_one_cumulative_limit(monkeypatch):
    import gzip
    monkeypatch.setattr(network, "MAX_BYTES", 64)
    data = gzip.compress(b"a" * 32) + gzip.compress(b"b" * 32)
    assert network.decode_body(data, "GZIP") == b"a" * 32 + b"b" * 32
    with pytest.raises(ValueError, match="Decompressed source exceeds"):
        network.decode_body(gzip.compress(b"a" * 33) + gzip.compress(b"b" * 32), "gzip")


def test_compressed_bomb_and_wire_size_are_bounded(monkeypatch):
    import gzip
    monkeypatch.setattr(network, "MAX_BYTES", 128)
    with pytest.raises(ValueError, match="Decompressed source exceeds"):
        network.decode_body(gzip.compress(b"a" * 10000), "gzip")
    with pytest.raises(ValueError, match="Source exceeds"):
        network.decode_body(b"a" * 129, "identity")


@pytest.mark.parametrize("data,encoding", [(b"invalid", "gzip"), (b"", "gzip"), (b"x", "br"), (b"x", "gzip, deflate")])
def test_invalid_or_unsupported_compression_is_readable(data, encoding):
    with pytest.raises(ValueError, match="compressed content"):
        network.decode_body(data, encoding)


def test_internal_network_and_mixed_dns_blocked(monkeypatch):
    for ip in ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "fd00::1"]:
        monkeypatch.setattr(
            socket, "getaddrinfo", lambda *a, _ip=ip, **kw: [(0, 0, 0, "", (_ip, 80))]
        )
        with pytest.raises(ValueError, match="blocked"):
            network.resolve_public("http://example.com")
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **kw: [
            (0, 0, 0, "", ("8.8.8.8", 80)),
            (0, 0, 0, "", ("127.0.0.1", 80)),
        ],
    )
    with pytest.raises(ValueError):
        network.resolve_public("http://example.com")


def test_redirect_internal_rechecked(monkeypatch):
    def dns(host, *a, **kw):
        return [
            (0, 0, 0, "", ("127.0.0.1" if host == "internal.test" else "8.8.8.8", 80))
        ]

    monkeypatch.setattr(socket, "getaddrinfo", dns)
    response = Mock(status=302)
    response.getheader.return_value = "http://internal.test"
    connection = Mock()
    connection.getresponse.return_value = response
    monkeypatch.setattr(
        network.http.client, "HTTPConnection", lambda *a, **kw: connection
    )
    with pytest.raises(ValueError, match="blocked"):
        network.fetch_html("http://public.test")
    assert connection.request.call_count == 1


def test_safe_faiss_restart(tmp_path, monkeypatch):
    from langchain_core.embeddings import Embeddings
    from langchain_core.documents import Document
    from langchain_community.vectorstores import FAISS

    class FakeEmbeddings(Embeddings):
        def embed_documents(self, texts):
            return [[float(len(t)), 1.0] for t in texts]

        def embed_query(self, text):
            return [float(len(text)), 1.0]

    embed = FakeEmbeddings()
    store = FAISS.from_documents(
        [
            Document(
                page_content="saved evidence",
                metadata={"source": "private.pdf", "chunk": 1},
            )
        ],
        embed,
    )
    save_index(store, tmp_path)
    import langchain_openai

    monkeypatch.setattr(langchain_openai, "OpenAIEmbeddings", lambda **kw: embed)
    restored = load_index(tmp_path, "test-key")
    assert (
        restored.similarity_search("saved evidence", k=4)[0].metadata["source"]
        == "private.pdf"
    )
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "documents.json",
        "index.faiss",
    ]


def test_real_ocr():
    from PIL import Image, ImageDraw, ImageFont
    from workflows.image_to_text import extract_text_from_image
    from io import BytesIO

    image = Image.new("RGB", (800, 160), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    draw.text((20, 40), "TRACE readable evidence", font=font, fill="black")
    data = BytesIO()
    image.save(data, format="PNG")
    data.seek(0)
    assert "TRACE" in extract_text_from_image(data)


def test_compiler_cannot_read_session_data(tmp_path):
    from backend.app import app
    from workflows.code_copilot import verify_code

    secret = tmp_path / "session-private.txt"
    secret.write_text("NEVER_EXPOSE_THIS_SESSION")
    result = verify_code(f'#include "{secret}"\nint main(void){{return 0;}}', "c")
    assert not result["passed"]
    diagnostics = " ".join(check["details"] for check in result["checks"])
    assert "NEVER_EXPOSE_THIS_SESSION" not in diagnostics
    if "kernel has no Landlock" in diagnostics:
        import os

        if os.environ.get("TRACE_REQUIRE_COMPILER_ISOLATION") == "1":
            pytest.fail("Native CI must support filesystem isolation")
        pytest.skip(
            "Landlock syscall is unavailable under cross-architecture emulation"
        )
    assert "Permission denied" in diagnostics
