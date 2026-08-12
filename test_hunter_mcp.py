import os

from anthropic import Anthropic
from dotenv import load_dotenv


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# HUNTER MCP TEST
# ---------------------------------------------------------

def test_hunter(company_domain: str):

    # Read credentials from .env
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    zapier_mcp_url = os.getenv("ZAPIER_MCP_URL")
    zapier_mcp_token = os.getenv("ZAPIER_MCP_TOKEN")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

    # -----------------------------------------------------
    # VALIDATE ENVIRONMENT VARIABLES
    # -----------------------------------------------------

    if not anthropic_api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing from your .env file."
        )

    if not zapier_mcp_url:
        raise ValueError(
            "ZAPIER_MCP_URL is missing from your .env file."
        )

    if not zapier_mcp_token:
        raise ValueError(
            "ZAPIER_MCP_TOKEN is missing from your .env file."
        )


    # -----------------------------------------------------
    # CREATE ANTHROPIC CLIENT
    # -----------------------------------------------------

    client = Anthropic(
        api_key=anthropic_api_key
    )


    # -----------------------------------------------------
    # CALL CLAUDE + ZAPIER MCP + HUNTER
    # -----------------------------------------------------

    response = client.beta.messages.create(

        model=model,

        max_tokens=4000,

        betas=[
            "mcp-client-2025-11-20"
        ],

        # Connect Claude to Zapier MCP
        mcp_servers=[
            {
                "type": "url",
                "url": zapier_mcp_url,
                "name": "zapier",
                "authorization_token": zapier_mcp_token,
            }
        ],

        # Give Claude access to tools inside Zapier MCP
        tools=[
            {
                "type": "mcp_toolset",
                "mcp_server_name": "zapier",
            }
        ],

        # -------------------------------------------------
        # CLAUDE INSTRUCTIONS
        # -------------------------------------------------

        system="""
You are testing a recruiter email discovery workflow.

You have access to a Webhooks by Zapier GET tool.

The webhook tool is already configured to call:

https://api.hunter.io/v2/domain-search

The Hunter API authentication and API key are already
configured securely inside Zapier.

Your job is to use Hunter to find professional recruiter,
talent acquisition, HR, or people-team contacts at the
company supplied by the user.


IMPORTANT RULES

Use the Webhooks by Zapier GET tool exactly ONCE.

Do NOT:
- change the API URL
- request another API endpoint
- request the Hunter API key
- expose authentication credentials
- make a second Hunter request
- invent names
- invent job titles
- invent email addresses
- invent LinkedIn URLs


HUNTER QUERY PARAMETERS

Generate these query parameters:

domain:
Use the company domain supplied by the user.

type:
personal

department:
hr

job_titles:
recruiter,technical recruiter,product recruiter,talent acquisition,talent acquisition partner,recruiting manager,recruiting lead

required_field:
full_name,position

verification_status:
valid

limit:
10


SEARCH GOAL

We specifically want people involved in hiring.

Prioritize contacts whose titles contain:

- Recruiter
- Technical Recruiter
- Product Recruiter
- Senior Recruiter
- Recruiting Manager
- Recruiting Lead
- Talent Acquisition
- Talent Acquisition Partner
- Talent Partner
- People Partner
- People Operations
- Human Resources
- HR


AFTER HUNTER RETURNS RESULTS

Return every relevant recruiting / HR contact.

For each person show:

1. First Name
2. Last Name
3. Job Title
4. Professional Email
5. Confidence Score
6. Verification Status
7. LinkedIn URL if available


If Hunter returns people who are NOT related to recruiting,
HR, talent acquisition, or people operations, do not present
them as recruiters.

If Hunter returns zero relevant recruiter or HR contacts,
say exactly:

"No recruiter contacts found for this company."

Only use information actually returned by Hunter.
""",

        # -------------------------------------------------
        # USER REQUEST
        # -------------------------------------------------

        messages=[
            {
                "role": "user",
                "content": (
                    f"Find recruiter, talent acquisition, or HR "
                    f"contacts at {company_domain}."
                ),
            }
        ],
    )


    # -----------------------------------------------------
    # DISPLAY RESPONSE
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("CLAUDE + ZAPIER MCP + HUNTER TEST")
    print("=" * 70)
    print()


    # Loop through everything Claude returned
    for block in response.content:

        block_type = getattr(
            block,
            "type",
            None
        )


        # -------------------------------------------------
        # CLAUDE TEXT RESPONSE
        # -------------------------------------------------

        if block_type == "text":

            print()
            print("[CLAUDE RESPONSE]")
            print("-" * 50)
            print()

            print(block.text)


        # -------------------------------------------------
        # MCP TOOL CALL
        # -------------------------------------------------

        elif block_type == "mcp_tool_use":

            print()
            print("[MCP TOOL CALL]")
            print("-" * 50)

            print(
                f"Tool: {block.name}"
            )

            print(
                f"Input: {block.input}"
            )


        # -------------------------------------------------
        # MCP TOOL RESULT
        # -------------------------------------------------

        elif block_type == "mcp_tool_result":

            print()
            print("[MCP TOOL RESULT]")
            print("-" * 50)

            print(
                f"Error: {block.is_error}"
            )

            print()
            print("Raw Hunter Result:")
            print()

            for item in block.content:

                if hasattr(item, "text"):

                    # Print up to 10,000 characters so we can
                    # inspect the Hunter response if needed.
                    print(
                        item.text[:10000]
                    )


# ---------------------------------------------------------
# RUN SCRIPT
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("Hunter Recruiter Search Test")
    print("============================")
    print()

    company_domain = input(
        "Enter company domain: "
    ).strip()


    # Basic input validation
    if not company_domain:

        print(
            "Please enter a company domain."
        )

    else:

        print()
        print(
            f"Searching Hunter for recruiters at "
            f"{company_domain}..."
        )
        print()

        try:

            test_hunter(
                company_domain
            )

        except Exception as error:

            print()
            print("ERROR")
            print("-" * 50)

            print(error)