from pathlib import Path
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
files = list(incoming.glob("*.txt"))

if not files:
    print("⚠️ No incoming TXT files found.")
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

        text = raw  # TXT는 그대로 사용

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
        print(f"❌ Error in {file.name}: {str(e)}")
        continue

print("\n🎉 Processing completed.")
