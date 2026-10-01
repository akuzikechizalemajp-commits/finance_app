import json

from openai import OpenAI
from dotenv import load_dotenv


# Load the API key from .env
load_dotenv()


client = OpenAI()


def analyze_tax_text(text):
    """
    Ask AI to extract tax rules from official NTA text
    and return them as structured JSON.
    """

    prompt = f"""
You are extracting Japanese tax rules from an official
National Tax Agency (NTA) source.

Your job is ONLY to extract information that is explicitly
supported by the supplied NTA text.

Do NOT invent, estimate, assume, or fill in missing information.

The "tax_type" field is an application classification.

If the source is Japanese income tax (所得税), return:
"income_tax"

If the source is Japanese resident tax (住民税), return:
"resident_tax"

If the source is Japanese social insurance (社会保険), return:
"social_insurance"

If the source does not clearly correspond to one of these
categories, return null.

Do not use Japanese tax names as the value of "tax_type".

Return ONLY valid JSON.

Use exactly this structure:

{{
  "tax_type": null,
  "source_reference_date": null,
  "tax_year": null,
  "effective_from": null,
  "effective_to": null,
  "brackets": [],
  "deductions": [],
  "special_rules": [],
  "future_changes": [],
  "uncertainties": []
}}

For "brackets", extract EVERY tax bracket explicitly stated
in the source. Do NOT assume a fixed number of brackets.

Each bracket should use:

{{
  "lower_limit": null,
  "upper_limit": null,
  "rate": null,
  "deduction": null,
  "description": null
}}

For "deductions", use:

{{
  "name": null,
  "amount": null,
  "description": null
}}

For "special_rules", use:

{{
  "name": null,
  "description": null,
  "effective_from": null
}}

For "future_changes", use:

{{
  "name": null,
  "description": null,
  "effective_from": null
}}

For "uncertainties", record any conflicting, ambiguous,
or unclear information found in the NTA text.

Important rules:

1. Extract information from the source only.
2. Never invent a tax year if the source does not explicitly
   identify one.
3. Do not assume that the number of brackets is fixed.
4. Preserve effective dates when they are stated.
5. Preserve exceptions and special rules.
6. If information is not stated, use null.
7. If the source contains conflicting information, put the
   conflict in "uncertainties".
8. Rates should be represented as decimal numbers.
   Example: 5% = 0.05.
9. All dates must be returned in ISO format YYYY-MM-DD.
For Japanese era dates, convert them to the corresponding
Gregorian calendar date.
Example: 令和8年4月1日 = 2026-04-01.
10. Monetary amounts should be represented as numbers without
   currency symbols or commas.
11. Return JSON only. Do not include Markdown.

NTA SOURCE TEXT:

{text}
"""

    print("TAX TYPE INSTRUCTION LOADED")

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    result = response.output_text

    # Convert the AI response from text into Python data.
    return json.loads(result)