from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype="float32",
    device_map="cpu"
)

summary = open(sys.argv[1]).read()

prompt = f"""
Rewrite the following extractive summary as a spoken-word podcast script.

Neutral tone.
No opinions.
No hype.
Plain English.
Target length: 4-6 minutes.

TEXT:
{summary}
"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=600,
    temperature=0.3,
    top_p=0.9
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
