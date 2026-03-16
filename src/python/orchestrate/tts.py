import io
import wave

from google import genai
from google.genai import types as genai_types


class TTS:

    AUDIO_MIME_TYPE_EXTENSIONS = {
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/mpeg": "mp3",
        "audio/flac": "flac",
        "audio/ogg": "ogg",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _generate_audio_with_gemini_sdk(script: str) -> tuple[bytes, str]:
        client = genai.Client(api_key=self.api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"A concise, clear podcast narrator:\n\n{script}",
            config=genai_types.GenerateContentConfig(response_modalities=["AUDIO"]),
        )

        audio_bytes, mime_type = _extract_audio_bytes(response)
        if not audio_bytes:
            raise AudioException("Gemini TTS response did not include audio bytes")
        return audio_bytes, mime_type

    def _extract_audio_bytes(response: object) -> tuple[bytes, str]:
        # SDK objects vary across versions, so handle object and dict-style payloads.
        candidates = getattr(response, "candidates", None)
        if candidates is None and isinstance(response, dict):
            candidates = response.get("candidates")

        for candidate in candidates or []:
            content = getattr(candidate, "content", None)
            if content is None and isinstance(candidate, dict):
                content = candidate.get("content")

            parts = getattr(content, "parts", None)
            if parts is None and isinstance(content, dict):
                parts = content.get("parts")

            for part in parts or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data is None and isinstance(part, dict):
                    inline_data = part.get("inlineData") or part.get("inline_data")

                if inline_data is None:
                    continue

                data = getattr(inline_data, "data", None)
                if data is None and isinstance(inline_data, dict):
                    data = inline_data.get("data")

                mime_type = getattr(inline_data, "mime_type", None)
                if mime_type is None:
                    mime_type = getattr(inline_data, "mimeType", None)
                if mime_type is None and isinstance(inline_data, dict):
                    mime_type = inline_data.get("mimeType") or inline_data.get(
                        "mime_type"
                    )

                if isinstance(data, bytes):
                    return data, str(mime_type or "")
                if isinstance(data, str):
                    return base64.b64decode(data), str(mime_type or "")

        return b"", ""

    def _pcm_l16_to_wav_bytes(audio_bytes: bytes, mime_type: str) -> bytes:
        sample_rate = 24000
        parts = [part.strip() for part in mime_type.split(";")]
        for part in parts:
            if part.startswith("rate="):
                try:
                    sample_rate = int(part.split("=", 1)[1])
                except ValueError:
                    pass

        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # L16 = 16-bit PCM
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_bytes)
            return wav_io.getvalue()
