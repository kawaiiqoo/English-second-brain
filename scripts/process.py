from pathlib import Path
import json
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

incoming = Path("incoming")
notes = Path("notes")

notes.mkdir(exist_ok=True)

for file in incoming.glob("*.json"):

    data = json.loads(file.read_text(
        encoding="utf-8"
    ))

    text = data["text"]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role":"system",
                "content":"""
You are an English learning assistant.

Return markdown:

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
                "role":"user",
                "content":text
            }
        ]
    )

    output = response.choices[0].message.content

    md_file = notes / f"{file.stem}.md"

    md_file.write_text(
        output,
        encoding="utf-8"
    )
