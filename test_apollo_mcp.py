import os

from anthropic import Anthropic
from dotenv import load_dotenv


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# TEST APOLLO THROUGH ZAPIER MCP
# ---------------------------------------------------------

def test_apollo(company_domain):

    # Get credentials from .env
    api_key = os.getenv("ANTHROPIC_API_KEY")
    mcp_url = os.getenv("ZAPIER_MCP_URL")
    mcp_token = os.getenv("ZAPIER_MCP_TOKEN")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing from .env"
        )

    if not mcp_url:
        raise ValueError(
            "ZAPIER_MCP_URL is missing from .env"
        )

    if not mcp_token:
        raise ValueError(
            "ZAPIER_MCP_TOKEN is missing from .env"
        )


    # -----------------------------------------------------
    # CREATE ANTHROPIC CLIENT
    # -----------------------------------------------------

    client = Anthropic(
        api_key=api_key
    )


    # -----------------------------------------------------
    # ASK CLAUDE TO USE APOLLO THROUGH ZAPIER MCP
    # -----------------------------------------------------

    response = client.beta.messages.create(

        model=model,

        max_tokens=3000,

        betas=[
            "mcp-client-2025-11-20"
        ],

        # Connect Claude to our Zapier MCP server
        mcp_servers=[
            {
                "type": "url",
                "url": mcp_url,
                "name": "zapier",
                "authorization_token": mcp_token,
            }
        ],

        # Allow Claude to use tools exposed by Zapier
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
You are testing an Apollo recruiter search workflow.

You have access to an Apollo API Request tool through Zapier MCP.

IMPORTANT:

The Apollo MCP tool has already been configured with:

HTTP METHOD:
POST

URL:
https://api.apollo.io/api/v1/mixed_people/api_search

DO NOT:
- change the endpoint
- use a GET request
- try another Apollo endpoint
- use /mixed_people/search
- put Markdown syntax around URLs
- invent recruiter information

Use the Apollo tool exactly once.


SEARCH GOAL:

Find up to 3 recruiters currently working at the company
domain supplied by the user.


USE THESE SEARCH FILTERS:

q_organization_domains_list[]:
Use the company domain supplied by the user.

person_titles[]:
- recruiter
- technical recruiter
- product recruiter
- talent acquisition
- talent acquisition partner

contact_email_status[]:
- verified

include_similar_titles:
true

page:
1

per_page:
3


RETURN:

For each person found, return:

- Apollo Person ID
- Name
- Job Title
- Company
- City
- State
- Country
- LinkedIn URL


IMPORTANT:

Apollo People Search does NOT return the actual email address.

Do not try to retrieve emails during this test.

We will perform email enrichment separately after
People Search is confirmed working.
""",

        messages=[
            {
                "role": "user",
                "content": (
                    f"Find up to 3 recruiters currently "
                    f"working at {company_domain}."
                ),
            }
        ],
    )


    # -----------------------------------------------------
    # PRINT RESULTS
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("CLAUDE + ZAPIER MCP + APOLLO TEST")
    print("=" * 60)
    print()


    for block in response.content:

        block_type = getattr(
            block,
            "type",
            None
        )


        # -------------------------------------------------
        # CLAUDE TEXT
        # -------------------------------------------------

        if block_type == "text":

            print("\n[CLAUDE RESPONSE]\n")

            print(block.text)


        # -------------------------------------------------
        # MCP TOOL CALL
        # -------------------------------------------------

        elif block_type == "mcp_tool_use":

            print("\n[MCP TOOL CALL]")

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

            print("\n[MCP TOOL RESULT]")

            print(
                f"Error: {block.is_error}"
            )

            print("\nResult:\n")

            for item in block.content:

                if hasattr(item, "text"):

                    print(
                        item.text[:5000]
                    )


# ---------------------------------------------------------
# RUN TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("Apollo Recruiter Search Test")
    print("-----------------------------")

    domain = input(
        "Enter company domain: "
    ).strip()

    print(
        f"\nSearching Apollo for recruiters at {domain}...\n"
    )

    test_apollo(domain)