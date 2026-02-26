import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Keys are read at call time (not module load) so .env changes take effect without restart
# Default model: gemini-1.5-flash (free tier) — swap to gemini-1.5-pro for higher quality

SYSTEM_PROMPT = """You are a senior business contract analyst with deep expertise in commercial law and risk assessment. 
Your task is to analyze contracts and return a precise, structured JSON response. 
Always base your analysis strictly on the text provided — do not invent or assume information not present.
If a field is not mentioned in the contract, use "Not specified" as the value.
Return ONLY valid JSON — no markdown, no explanation, no commentary outside the JSON object."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze the following contract and return a JSON response in exactly this format:

{{
  "plain_english_summary": "1 paragraph summary understandable by a non-lawyer",

  "key_parties": {{
    "party_1": "",
    "party_2": "",
    "other_parties": []
  }},

  "contract_duration": {{
    "start_date": "",
    "end_date": "",
    "renewal_terms": "",
    "auto_renewal": "Yes/No/Not Found"
  }},

  "payment_terms": {{
    "amounts": "",
    "payment_schedule": "",
    "late_fees": "",
    "refund_policy": ""
  }},

  "termination_clauses": {{
    "termination_for_convenience": "",
    "termination_for_cause": "",
    "notice_period": "",
    "exit_conditions": ""
  }},

  "confidentiality_terms": "",
  "intellectual_property_terms": "",
  
  "liability_and_indemnity": {{
    "liability_cap": "",
    "indemnification_clause": ""
  }},

  "risk_flags": [
    {{
      "category": "Auto-Renewal Risk",
      "risk_level": "Low/Medium/High",
      "reason": "",
      "clause_reference": ""
    }},
    {{
      "category": "Liability Risk",
      "risk_level": "Low/Medium/High",
      "reason": "",
      "clause_reference": ""
    }},
    {{
      "category": "Exit Risk",
      "risk_level": "Low/Medium/High",
      "reason": "",
      "clause_reference": ""
    }},
    {{
      "category": "Payment Risk",
      "risk_level": "Low/Medium/High",
      "reason": "",
      "clause_reference": ""
    }},
    {{
      "category": "IP Risk",
      "risk_level": "Low/Medium/High",
      "reason": "",
      "clause_reference": ""
    }}
  ],

  "unusual_or_risky_clauses": [
    {{
      "clause": "",
      "why_it_is_risky": ""
    }}
  ]
}}

CONTRACT TEXT:
---
{contract_text}
---

Return only the JSON object. No other text."""


def analyze_contract(contract_text: str) -> dict:
    """
    Send the contract text to Gemini and return the parsed JSON analysis.
    Raises Exception on API error or JSON parse failure.
    """
    # Read at call-time so .env changes don't require a server restart
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Get a free key at https://aistudio.google.com/app/apikey "
            "and add it to backend/.env"
        )

    # Cap contract text to ~80,000 characters to stay within token limits
    MAX_CHARS = 80_000
    if len(contract_text) > MAX_CHARS:
        contract_text = contract_text[:MAX_CHARS] + "\n\n[NOTE: Contract was truncated to fit token limits.]"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            max_output_tokens=4096,
            temperature=0.1,   # Low temp for consistent structured output
        )
    )

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(contract_text=contract_text)
    response = model.generate_content(prompt)
    raw_response = response.text.strip()

    # Strip markdown code fences if Claude wraps the JSON
    if raw_response.startswith("```"):
        lines = raw_response.split("\n")
        # Remove first and last lines (the ``` fences)
        raw_response = "\n".join(lines[1:-1]).strip()

    try:
        analysis = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude returned an invalid JSON response. Parse error: {str(e)}\n"
            f"Raw response: {raw_response[:500]}"
        )

    return analysis
