from pathlib import Path
import json
from openai import OpenAI
import os
import sys

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
incoming = BASE_DIR / "incoming"
notes = BASE_DIR / "notes"

notes.mkdir(exist_ok=True)

# -------------------------
# Safety check
# -------------------------
files = list(incoming.glob("*.json"))

if not files:
    print("⚠️ No incoming JSON files found.")
    sys.exit(0)

print(f"📦 Found {len(files)} files")

# -------------------------
# Process loop
# -------------------------
for file in files:
    try:
        print(f"\n🔹 Processing: {file.name}")

        raw = file.read_text(encoding="utf-8").strip()

        if not raw:
            print(f"⚠️ Empty file skipped: {file.name}")
            continue

        # -------------------------
        # JSON parse
        # -------------------------
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(f"❌ JSON error in file: {file.name}")
            continue

        # -------------------------
        # TEXT extraction (FIX 핵심)
        # -------------------------
        text = data.get("text") or data.get("Text") or ""

        text = text.strip()

        if not text:
            print(f"⚠️ No valid text in: {file.name}")
            continue

        print(f"🧠 Input length: {len(text)} chars")

        # -------------------------
        # GPT Call
        # -------------------------
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an English learning assistant.

Return markdown strictly:

---
date:
topic:
difficulty:
---

# expression

## Meaning

## Example

## Related Expressions
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        output = response.choices[0].message.content

        # -------------------------
        # Save output
        # -------------------------
        out_file = notes / f"{file.stem}.md"
        out_file.write_text(output, encoding="utf-8")

        print(f"✅ Saved: {out_file.name}")

    except Exception as e:
        print(f"❌ Unexpected error in {file.name}: {str(e)}")
        continue

print("\n🎉 Processing completed.")
