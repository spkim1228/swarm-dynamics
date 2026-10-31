from typing import Literal

import ollama
from pydantic import BaseModel

MODEL = "llama3.1:8b"

PROMPT = """Rate the text below on two scales from 1 to 5.

prosocial: 1 = hostile, selfish or harmful to others; 3 = neutral; 5 = cooperative, helpful or caring toward others.
conformist: 1 = defies norms, rules or the group; 3 = neutral; 5 = defers to norms, rules, authority or the group.

Text:
\"\"\"
{text}
\"\"\""""


class Leaning(BaseModel):
    prosocial: Literal[1, 2, 3, 4, 5]
    conformist: Literal[1, 2, 3, 4, 5]


def score(text: str, model: str = MODEL, num_ctx: int | None = None) -> dict:
    """Score text for prosocial and conformist leanings (1-5 each) with a local Ollama model."""
    resp = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        format=Leaning.model_json_schema(),
        options={"temperature": 0} | ({"num_ctx": num_ctx} if num_ctx else {}),
    )
    return Leaning.model_validate_json(resp.message.content or "").model_dump()


if __name__ == "__main__":
    print(score("Let's all follow the house rules and help each other keep the wiki tidy."))
