import base64
from pathlib import Path
import sys
from types import SimpleNamespace

from click.testing import CliRunner
import click

# Keep tests runnable directly from the workspace without editable install.
SRC_PYTHON = Path(__file__).resolve().parents[1] / "src" / "python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.append(str(SRC_PYTHON))

from orchestrate import cli


def test_extract_audio_bytes_from_dict_inline_data_base64() -> None:
    raw = b"mp3-bytes"
    encoded = base64.b64encode(raw).decode("ascii")
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"inlineData": {"data": encoded, "mimeType": "audio/mpeg"}}
                    ]
                }
            }
        ]
    }

    audio_bytes, mime_type = cli._extract_audio_bytes(response)
    assert audio_bytes == raw
    assert mime_type == "audio/mpeg"


def test_extract_audio_bytes_from_object_inline_data_bytes() -> None:
    raw = b"audio-payload"
    part = SimpleNamespace(
        inline_data=SimpleNamespace(data=raw, mime_type="audio/mpeg")
    )
    content = SimpleNamespace(parts=[part])
    response = SimpleNamespace(candidates=[SimpleNamespace(content=content)])

    audio_bytes, mime_type = cli._extract_audio_bytes(response)
    assert audio_bytes == raw
    assert mime_type == "audio/mpeg"


def test_pcm_l16_to_wav_bytes_has_wav_header() -> None:
    pcm = b"\x00\x00\x01\x00\xff\x7f\x00\x80"
    wav_bytes = cli._pcm_l16_to_wav_bytes(pcm, "audio/L16;codec=pcm;rate=24000")

    assert wav_bytes.startswith(b"RIFF")
    assert b"WAVE" in wav_bytes[:16]


def test_generate_audio_with_gemini_sdk_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    try:
        cli._generate_audio_with_gemini_sdk("script")
        assert False, "expected ClickException"
    except click.ClickException as exc:
        assert "GOOGLE_API_KEY is not set" in str(exc)


def test_main_writes_audio_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli,
        "b",
        SimpleNamespace(ExtractArticle=lambda url: SimpleNamespace(script="summary")),
    )
    monkeypatch.setattr(
        cli,
        "_generate_audio_with_gemini_sdk",
        lambda script: (b"fake-mp3-data", "audio/mpeg"),
    )

    output_file = tmp_path / "podcast.mp3"
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["https://example.com/article", "-o", str(output_file)]
    )

    assert result.exit_code == 0, result.output
    assert output_file.exists()
    assert output_file.read_bytes() == b"fake-mp3-data"


def test_main_rewrites_extension_for_wav_content(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli,
        "b",
        SimpleNamespace(ExtractArticle=lambda url: SimpleNamespace(script="summary")),
    )
    monkeypatch.setattr(
        cli,
        "_generate_audio_with_gemini_sdk",
        lambda script: (b"\x00\x00\x01\x00", "audio/L16;codec=pcm;rate=24000"),
    )

    requested_file = tmp_path / "podcast.mp3"
    expected_file = tmp_path / "podcast.wav"
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["https://example.com/article", "-o", str(requested_file)]
    )

    assert result.exit_code == 0, result.output
    assert not requested_file.exists()
    assert expected_file.exists()
    assert expected_file.read_bytes().startswith(b"RIFF")
