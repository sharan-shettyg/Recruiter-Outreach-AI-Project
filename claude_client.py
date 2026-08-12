import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def _extract_json(text: str) -> dict:
    """Parse a JSON object even if the model wraps it in markdown fences."""
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Claude did not return valid JSON.")
        return json.loads(match.group(0))


def generate_outreach(
    resume_text: str,
    job_description: str,
    recruiter_name: str,
    recruiter_email: str,
    company: str,
    job_title: str,
) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing. Add it to your .env file."
        )

    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
    client = Anthropic(api_key=api_key)

    system_prompt = """
You are an expert career outreach assistant.

Write a concise, professional recruiter outreach email for a job seeker.

Rules:
- Use ONLY facts supported by the supplied resume and job description.
- Never invent skills, achievements, employers, years of experience, referrals, or credentials.
- Personalize the message to the specific role and company.
- Mention 2-3 highly relevant candidate strengths.
- Keep the email body between 90 and 150 words.
- Sound human and confident, not desperate or overly salesy.
- Do not claim the recruiter owns the role unless that is explicitly known.
- End with a simple request to connect or discuss fit.
- Return ONLY valid JSON, with no markdown.

Return this exact shape:
{
  "subject": "email subject",
  "body": "plain-text email body",
  "match_score": 0,
  "match_reason": "1-2 sentence explanation",
  "strengths": ["strength 1", "strength 2", "strength 3"]
}
"""

    user_prompt = f"""
CANDIDATE RESUME:
{resume_text}

JOB:
Company: {company}
Title: {job_title}

JOB DESCRIPTION:
{job_description}

RECRUITER:
Name: {recruiter_name}
Email: {recruiter_email}
"""

    response = client.messages.create(
        model=model,
        max_tokens=1200,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    text_blocks = [
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]
    if not text_blocks:
        raise ValueError("Claude returned no text response.")

    result = _extract_json("\n".join(text_blocks))

    required = {"subject", "body", "match_score", "match_reason", "strengths"}
    missing = required - result.keys()
    if missing:
        raise ValueError(f"Claude response is missing: {', '.join(sorted(missing))}")

    return result
