import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# CONFIG
# =========================================================

# This is the expected internal MCP tool name for:
# Webhooks by Zapier -> POST
#
# If Zapier exposes a different internal name, you only
# need to change this one value.
HUNTER_POST_TOOL_NAME = os.getenv(
    "HUNTER_POST_TOOL_NAME",
    "webhooks_by_zapier_post",
)


# =========================================================
# HELPERS
# =========================================================

def _clean_email(value: str) -> str:
    """
    Extract a normal email address.

    Handles values such as:
    [john@company.com](mailto:john@company.com)
    """

    if not value:
        return ""

    match = re.search(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        str(value),
    )

    if match:
        return match.group(0).strip()

    return str(value).strip()


def _clean_url(value: str) -> str:
    """
    Extract a normal URL from possible Markdown formatting.
    """

    if not value:
        return ""

    match = re.search(
        r"https?://[^\s\]\)]+",
        str(value),
    )

    if match:
        return match.group(0).strip()

    return str(value).strip()


def _extract_json(text: str):
    """
    Attempt to parse JSON returned by Zapier MCP.
    """

    if not text:
        return None

    text = text.strip()

    # -----------------------------------------------------
    # NORMAL JSON
    # -----------------------------------------------------

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass


    # -----------------------------------------------------
    # JSON INSIDE CODE BLOCK
    # -----------------------------------------------------

    code_block = re.search(
        r"```(?:json)?\s*(.*?)```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if code_block:

        try:
            return json.loads(
                code_block.group(1).strip()
            )

        except json.JSONDecodeError:
            pass


    # -----------------------------------------------------
    # JSON EMBEDDED IN OTHER TEXT
    # -----------------------------------------------------

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if match:

        try:
            return json.loads(
                match.group(0)
            )

        except json.JSONDecodeError:
            pass


    return None


def _extract_tool_error(block) -> str:
    """
    Pull readable error text from an MCP tool result.
    """

    messages = []

    content = getattr(
        block,
        "content",
        [],
    )

    for item in content:

        text = getattr(
            item,
            "text",
            None,
        )

        if text:
            messages.append(text)

    if messages:
        return "\n".join(messages)

    return "Unknown MCP tool error."


# =========================================================
# FIND RECRUITERS
# =========================================================

def find_recruiters(
    company_domain: str,
    country_code: str,
):
    """
    Find recruiting contacts at a company using:

    Streamlit
        ->
    Claude
        ->
    Zapier MCP
        ->
    Webhooks by Zapier POST
        ->
    Hunter Domain Search

    Example:

        find_recruiters(
            "deloitte.com",
            "US"
        )
    """

    # =====================================================
    # LOAD SETTINGS
    # =====================================================

    anthropic_api_key = os.getenv(
        "ANTHROPIC_API_KEY"
    )

    zapier_mcp_url = os.getenv(
        "ZAPIER_MCP_URL"
    )

    zapier_mcp_token = os.getenv(
        "ZAPIER_MCP_TOKEN"
    )

    model = os.getenv(
        "CLAUDE_MODEL",
        "claude-sonnet-5",
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if not anthropic_api_key:

        raise ValueError(
            "ANTHROPIC_API_KEY is missing from .env"
        )


    if not zapier_mcp_url:

        raise ValueError(
            "ZAPIER_MCP_URL is missing from .env"
        )


    if not zapier_mcp_token:

        raise ValueError(
            "ZAPIER_MCP_TOKEN is missing from .env"
        )


    company_domain = (
        company_domain
        .strip()
        .lower()
    )


    country_code = (
        country_code
        .strip()
        .upper()
    )


    if not company_domain:

        raise ValueError(
            "Company domain is required."
        )


    if (
        len(country_code) != 2
        or not country_code.isalpha()
    ):

        raise ValueError(
            "Country code must be a two-letter code "
            "such as US, IN, GB, or CA."
        )


    # =====================================================
    # CLAUDE CLIENT
    # =====================================================

    client = Anthropic(
        api_key=anthropic_api_key
    )


    # =====================================================
    # CALL ZAPIER MCP
    # =====================================================

    response = client.beta.messages.create(

        model=model,

        max_tokens=4000,

        betas=[
            "mcp-client-2025-11-20"
        ],


        # -------------------------------------------------
        # CONNECT ZAPIER MCP
        # -------------------------------------------------

        mcp_servers=[
            {
                "type": "url",
                "url": zapier_mcp_url,
                "name": "zapier",
                "authorization_token": zapier_mcp_token,
            }
        ],


        # -------------------------------------------------
        # CRITICAL SAFETY FIX
        #
        # Disable ALL Zapier tools.
        # Enable ONLY Webhooks POST.
        #
        # This prevents Claude from accidentally using:
        #
        # gmail_create_draft
        # gmail_send_email
        # Hunter Find Email
        # or any other MCP action.
        # -------------------------------------------------

        tools=[
            {
                "type": "mcp_toolset",

                "mcp_server_name": "zapier",

                "default_config": {
                    "enabled": False
                },

                "configs": {
                    HUNTER_POST_TOOL_NAME: {
                        "enabled": True
                    }
                },
            }
        ],


        # -------------------------------------------------
        # SYSTEM PROMPT
        # -------------------------------------------------

        system=f"""
You are a recruiter-discovery agent.

Your only job is to find recruiting contacts
using Hunter Domain Search.

You have access to exactly ONE permitted tool:

{HUNTER_POST_TOOL_NAME}

That tool is a Webhooks by Zapier POST action
already configured to call:

https://api.hunter.io/v2/domain-search

Authentication is already securely configured
inside Zapier.

You MUST use that POST tool exactly once.

NEVER use Gmail.

NEVER:
- create a Gmail draft
- send an email
- call another Zapier tool
- use Hunter Find Email
- ask for the Hunter API key
- reveal credentials
- invent names
- invent email addresses
- invent recruiter locations
- make more than one API request


=========================================================
HUNTER DOMAIN SEARCH REQUEST
=========================================================

Send a JSON body using this structure:

{{
    "domain": "COMPANY_DOMAIN",

    "type": "personal",

    "department": "hr",

    "job_titles": "recruiter,technical recruiter,product recruiter,senior recruiter,talent acquisition,talent acquisition partner,talent partner,recruiting manager,recruiting lead,recruiting coordinator,recruitment consultant,recruitment executive,corporate recruiter",

    "required_field": "full_name,position",

    "verification_status": "valid",

    "location": {{
        "include": [
            {{
                "country": "COUNTRY_CODE"
            }}
        ]
    }},

    "limit": 10
}}


Replace:

COMPANY_DOMAIN
with the exact company domain supplied by the user.

Replace:

COUNTRY_CODE
with the exact two-letter country code supplied by the user.


=========================================================
RULES
=========================================================

Only return contacts that Hunter actually returns.

Prioritize people whose roles relate to:

- Recruiter
- Senior Recruiter
- Technical Recruiter
- Product Recruiter
- Corporate Recruiter
- Talent Acquisition
- Talent Partner
- Recruiting Manager
- Recruiting Lead
- Recruiting Coordinator
- Recruitment Consultant
- Recruitment Executive
- HR recruiting

Do not substitute engineers, executives,
salespeople, consultants, or unrelated employees.

If Hunter finds zero matching recruiters,
return zero results. Do not invent contacts.
""",


        # -------------------------------------------------
        # USER REQUEST
        # -------------------------------------------------

        messages=[
            {
                "role": "user",

                "content": f"""
Search Hunter for recruiters.

Company domain:
{company_domain}

Country:
{country_code}

Use the permitted Webhooks by Zapier POST tool
exactly once.

Return Hunter's response.
"""
            }
        ],
    )


    # =====================================================
    # READ MCP RESPONSE
    # =====================================================

    raw_result = None

    tool_called = False


    for block in response.content:

        block_type = getattr(
            block,
            "type",
            None,
        )


        # -------------------------------------------------
        # CHECK WHICH TOOL CLAUDE USED
        # -------------------------------------------------

        if block_type == "mcp_tool_use":

            tool_called = True

            tool_name = getattr(
                block,
                "name",
                "",
            )


            if (
                tool_name
                != HUNTER_POST_TOOL_NAME
            ):

                raise ValueError(
                    "Unexpected MCP tool used: "
                    f"{tool_name}"
                )


        # -------------------------------------------------
        # TOOL RESULT
        # -------------------------------------------------

        if block_type == "mcp_tool_result":

            if getattr(
                block,
                "is_error",
                False,
            ):

                error_message = (
                    _extract_tool_error(
                        block
                    )
                )

                raise ValueError(
                    "Hunter MCP error: "
                    f"{error_message}"
                )


            content = getattr(
                block,
                "content",
                [],
            )


            for item in content:

                text = getattr(
                    item,
                    "text",
                    None,
                )


                if not text:
                    continue


                parsed = _extract_json(
                    text
                )


                if parsed is not None:

                    raw_result = parsed

                    break


    # =====================================================
    # VALIDATE TOOL EXECUTION
    # =====================================================

    if not tool_called:

        raise ValueError(
            "Claude did not call the Hunter "
            "Webhooks POST tool."
        )


    if raw_result is None:

        raise ValueError(
            "Hunter completed, but no structured "
            "JSON response was returned."
        )


    # =====================================================
    # FIND PEOPLE ARRAY
    # =====================================================

    people = []


    # -----------------------------------------------------
    # FORMAT 1
    #
    # {
    #     "results": [...]
    # }
    # -----------------------------------------------------

    if (
        isinstance(raw_result, dict)
        and isinstance(
            raw_result.get("results"),
            list,
        )
    ):

        people = raw_result[
            "results"
        ]


    # -----------------------------------------------------
    # FORMAT 2 - RAW HUNTER RESPONSE
    #
    # {
    #     "data": {
    #         "emails": [...]
    #     }
    # }
    # -----------------------------------------------------

    elif (
        isinstance(raw_result, dict)
        and isinstance(
            raw_result.get("data"),
            dict,
        )
    ):

        people = (
            raw_result
            .get("data", {})
            .get("emails", [])
        )


    # -----------------------------------------------------
    # FORMAT 3
    #
    # Sometimes Zapier may return nested data.
    # -----------------------------------------------------

    elif (
        isinstance(raw_result, dict)
        and isinstance(
            raw_result.get("emails"),
            list,
        )
    ):

        people = raw_result[
            "emails"
        ]


    # -----------------------------------------------------
    # NO CONTACTS
    # -----------------------------------------------------

    if not people:

        return []


    # =====================================================
    # NORMALIZE RECRUITERS
    # =====================================================

    recruiters = []


    for person in people:

        if not isinstance(
            person,
            dict,
        ):

            continue


        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        full_name = (
            person.get("full_name")
            or ""
        )


        first_name = (
            person.get("first_name")
            or ""
        )


        last_name = (
            person.get("last_name")
            or ""
        )


        if not full_name:

            full_name = (
                f"{first_name} {last_name}"
            ).strip()


        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = (
            person.get("position")
            or person.get("title")
            or ""
        )


        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        email = _clean_email(

            person.get("email")

            or person.get("value")

            or ""
        )


        if not email:
            continue


        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        confidence = (

            person.get("confidence")

            or person.get(
                "confidence_score"
            )

            or 0
        )


        try:

            confidence = int(
                confidence
            )

        except (
            ValueError,
            TypeError,
        ):

            confidence = 0


        # -------------------------------------------------
        # VERIFICATION
        # -------------------------------------------------

        verification_status = (
            person.get(
                "verification_status"
            )
            or ""
        )


        verification = (
            person.get(
                "verification"
            )
        )


        if (
            not verification_status
            and isinstance(
                verification,
                dict,
            )
        ):

            verification_status = (
                verification.get(
                    "status",
                    "",
                )
            )


        # -------------------------------------------------
        # LINKEDIN
        # -------------------------------------------------

        linkedin_url = _clean_url(

            person.get(
                "linkedin_url"
            )

            or person.get(
                "linkedin"
            )

            or ""
        )


        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        city = (
            person.get("city")
            or ""
        )


        state = (
            person.get("state")
            or ""
        )


        country = (
            person.get("country")
            or ""
        )


        location = (
            person.get(
                "location"
            )
        )


        if isinstance(
            location,
            dict,
        ):

            city = (
                city
                or location.get(
                    "city",
                    "",
                )
            )


            state = (
                state
                or location.get(
                    "state",
                    "",
                )
            )


            country = (
                country
                or location.get(
                    "country",
                    "",
                )
            )


        # -------------------------------------------------
        # NORMALIZED RESULT
        # -------------------------------------------------

        recruiters.append(
            {
                "name": full_name,

                "title": title,

                "email": email,

                "confidence": confidence,

                "verification_status": (
                    verification_status
                    or "valid"
                ),

                "linkedin_url": linkedin_url,

                "city": city,

                "state": state,

                "country": country,
            }
        )


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique = {}


    for recruiter in recruiters:

        email = (
            recruiter[
                "email"
            ]
            .lower()
            .strip()
        )

        unique[email] = recruiter


    return list(
        unique.values()
    )