import json
from openai import OpenAI


def _naive_extraction_prompt(text: str):
    return f"""
Extract entities and relationships from the following text.

Return ONLY valid JSON in this format:
{{
  "entities": [{{"id": "...", "type": "..."}}],
  "relations": [{{"source": "...", "target": "...", "relation": "..."}}]
}}

Always call entities and relations with an appropriate name;
do not use abbreviations such as "E" or "entity", the name must be an identifier

TEXT:
{text}
"""


class Model():

    def __init__(self, api_key=None):
        if api_key is None:
            self.client = OpenAI()
        else:
            self.client = OpenAI(api_key=api_key)

    def extract(self, text, prompt_builder=_naive_extraction_prompt):
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt_builder(text)}],
            temperature=0
        )

        content = response.choices[0].message.content
        cleaned_content = content.replace("\n", "").strip("` json")

        return json.loads(cleaned_content)
