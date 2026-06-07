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

        data = json.loads(raw)

        text = data.get("text")

        if not text:
            print(f"⚠️ No 'text' field in: {file.name}")
            continue

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

    except json.JSONDecodeError:
        print(f"❌ JSON error in file: {file.name}")
        continue

    except Exception as e:
        print(f"❌ Unexpected error in {file.name}: {str(e)}")
        continue

print("\n🎉 Processing completed.")
