import sys
from TTS.api import TTS

text_file = sys.argv[1]
out_file = sys.argv[2]

text = open(text_file).read()

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    progress_bar=False,
    gpu=False
)

tts.tts_to_file(
    text=text,
    speaker="Brian",      # stable default
    language="en",
    file_path=out_file
)