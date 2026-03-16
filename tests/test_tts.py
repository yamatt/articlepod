import base64
import io
import wave
from types import SimpleNamespace

import click
import pytest

from orchestrate.exceptions import AudioException
from orchestrate.tts import TTS


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

    audio_bytes, mime_type = TTS._extract_audio_bytes(response)
    assert audio_bytes == raw
    assert mime_type == "audio/mpeg"


def test_extract_audio_bytes_from_object_inline_data_bytes() -> None:
    raw = b"audio-payload"
    part = SimpleNamespace(
        inline_data=SimpleNamespace(data=raw, mime_type="audio/mpeg")
    )
    content = SimpleNamespace(parts=[part])
    response = SimpleNamespace(candidates=[SimpleNamespace(content=content)])

    audio_bytes, mime_type = TTS._extract_audio_bytes(response)
    assert audio_bytes == raw
    assert mime_type == "audio/mpeg"


def test_extract_audio_bytes_returns_empty_when_missing_audio() -> None:
    response = {"candidates": [{"content": {"parts": [{"text": "no audio"}]}}]}

    audio_bytes, mime_type = TTS._extract_audio_bytes(response)
    assert audio_bytes == b""
    assert mime_type == ""


def test_pcm_l16_to_wav_bytes_has_wav_header_and_rate() -> None:
    pcm = b"\x00\x00\x01\x00\xff\x7f\x00\x80"
    wav_bytes = TTS._pcm_l16_to_wav_bytes(pcm, "audio/L16;codec=pcm;rate=22050")

    assert wav_bytes.startswith(b"RIFF")
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getframerate() == 22050
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2


def test_generate_audio_with_gemini_sdk_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(click.ClickException, match="GOOGLE_API_KEY is not set"):
        TTS._generate_audio_with_gemini_sdk("script")


def test_generate_audio_with_gemini_sdk_raises_when_no_audio(monkeypatch) -> None:
    class FakeModels:
        @staticmethod
        def generate_content(**kwargs):
            return {"candidates": [{"content": {"parts": [{"text": "none"}]}}]}

    class FakeClient:
        def __init__(self, api_key: str):
            self.models = FakeModels()

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr("orchestrate.tts.genai.Client", FakeClient)

    with pytest.raises(AudioException, match="did not include audio bytes"):
        TTS._generate_audio_with_gemini_sdk("script")


def test_generate_audio_with_gemini_sdk_returns_audio(monkeypatch) -> None:
    raw = b"audio-bytes"

    class FakeModels:
        @staticmethod
        def generate_content(**kwargs):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "data": base64.b64encode(raw).decode("ascii"),
                                        "mimeType": "audio/mpeg",
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

    class FakeClient:
        def __init__(self, api_key: str):
            self.models = FakeModels()

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr("orchestrate.tts.genai.Client", FakeClient)

    audio_bytes, mime_type = TTS._generate_audio_with_gemini_sdk("script")

    assert audio_bytes == raw
    assert mime_type == "audio/mpeg"
