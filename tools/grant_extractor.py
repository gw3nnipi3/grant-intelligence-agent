import requests
import json
import re


class GrantExtractor:
    def __init__(self, model="llama3"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def extract_grants(self, email_text: str):

        prompt = f"""
You are a STRICT JSON EXTRACTION ENGINE.

You do NOT:
- explain
- chat
- summarise
- think out loud
- add commentary

ONLY OUTPUT VALID JSON.

-----------------------
TASK
-----------------------
Extract ALL grant / funding opportunities from the text.

A grant MUST include funding or application for money/support.

IGNORE:
- events
- competitions
- tickets
- newsletters
- general announcements without funding

-----------------------
OUTPUT RULES (HARD)
-----------------------
- Output MUST be valid JSON only
- No markdown
- No code blocks
- No text before or after JSON
- If no grants exist, return: {{"grants": []}}

-----------------------
LINK RULE (IMPORTANT)
-----------------------
- ALWAYS provide a link if ANY URL exists in text
- If multiple URLs exist, pick the official application or info page
- If no URL exists, set:
  "link": "requires_manual_search"

DO NOT leave link empty.

-----------------------
CATEGORY SYSTEM (STRICT)
-----------------------
Choose ONLY ONE:

SPORT
YOUTH
COMMUNITY
EDUCATION
HEALTH
MENTAL_HEALTH
SOCIAL_IMPACT
CAPITAL_PROJECTS
RESEARCH
ARTS
CORPORATE_FUNDING
NATIONAL_FUND
LOCAL_GOVERNMENT
OTHER

Never invent new categories.

-----------------------
FIT SCORE (SIMPLIFIED)
-----------------------
Score: 0-100 integer ONLY

Meaning:
- 90-100 = extremely relevant to grassroots UK basketball/youth sport
- 70-89 = relevant community/youth funding
- 40-69 = partially relevant
- 0-39 = weak relevance

-----------------------
OUTPUT FORMAT
-----------------------
{{
  "grants": [
    {{
      "title": "",
      "provider": "",
      "category": "",
      "amount": "",
      "deadline": "",
      "eligibility": "",
      "link": "",
      "fit_score": 0
    }}
  ]
}}

-----------------------
TEXT
-----------------------
{email_text}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 1200
                }
            },
            timeout=120
        )

        if response.status_code != 200:
            return {"grants": [], "error": response.text}

        raw = response.json().get("response", "")

        parsed = self._safe_json_extract(raw)
        if parsed:
            return self._validate(parsed)

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            parsed = self._safe_json_extract(match.group())
            if parsed:
                return self._validate(parsed)

        return {
            "grants": [],
            "raw_output": raw,
            "error": "Failed to parse JSON output"
        }

    def _safe_json_extract(self, text):
        try:
            return json.loads(text)
        except:
            return None

    def _validate(self, data):
        if not isinstance(data, dict):
            return {"grants": []}

        grants = data.get("grants", [])
        if not isinstance(grants, list):
            return {"grants": []}

        clean = []

        for g in grants:
            if not isinstance(g, dict):
                continue

            clean.append({
                "title": g.get("title", ""),
                "provider": g.get("provider", ""),
                "category": g.get("category", "OTHER"),
                "amount": g.get("amount", ""),
                "deadline": g.get("deadline", ""),
                "eligibility": g.get("eligibility", ""),
                "link": g.get("link", "requires_manual_search"),
                "fit_score": int(g.get("fit_score", 0) or 0)
            })

        return {"grants": clean}