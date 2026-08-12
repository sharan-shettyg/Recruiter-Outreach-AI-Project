import os

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

def _get_settings():

    api_key = os.getenv(
        "ANTHROPIC_API_KEY"
    )

    mcp_url = os.getenv(
        "ZAPIER_MCP_URL"
    )

    mcp_token = os.getenv(
        "ZAPIER_MCP_TOKEN"
    )

    model = os.getenv(
        "CLAUDE_MODEL",
        "claude-sonnet-5",
    )


    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is missing."
        )

    if not mcp_url:
        raise ValueError(
            "ZAPIER_MCP_URL is missing."
        )

    if not mcp_token:
        raise ValueError(
            "ZAPIER_MCP_TOKEN is missing."
        )


    return (
        api_key,
        mcp_url,
        mcp_token,
        model,
    )


# ---------------------------------------------------------
# EXECUTE GMAIL ACTION
# ---------------------------------------------------------

def _execute_gmail_action(
    action: str,
    to_email: str,
    subject: str,
    body: str,
):

    (
        api_key,
        mcp_url,
        mcp_token,
        model,
    ) = _get_settings()


    client = Anthropic(
        api_key=api_key
    )


    # -----------------------------------------------------
    # CHOOSE ACTION
    # -----------------------------------------------------

    if action == "draft":

        instruction = """
Use the Gmail Create Draft tool.

Create exactly ONE Gmail draft.

Do NOT send the email.
"""

        expected_words = [
            "gmail",
            "draft",
        ]


    elif action == "send":

        instruction = """
Use the Gmail Send Email tool.

Send exactly ONE email.
"""

        expected_words = [
            "gmail",
            "send",
        ]


    else:

        raise ValueError(
            f"Unsupported Gmail action: {action}"
        )


    # -----------------------------------------------------
    # CALL ZAPIER MCP
    # -----------------------------------------------------

    response = client.beta.messages.create(

        model=model,

        max_tokens=1500,

        betas=[
            "mcp-client-2025-11-20"
        ],

        mcp_servers=[
            {
                "type": "url",
                "url": mcp_url,
                "name": "zapier",
                "authorization_token": mcp_token,
            }
        ],

        tools=[
            {
                "type": "mcp_toolset",
                "mcp_server_name": "zapier",
            }
        ],

        system=f"""
You are executing a user-approved Gmail action.

{instruction}

IMPORTANT RULES:

- Use only the appropriate Gmail tool.
- Do not use Hunter.
- Do not use Webhooks.
- Do not modify the recipient.
- Do not modify the subject.
- Do not modify the body.
- Do not add CC recipients.
- Do not add BCC recipients.
- Do not attach any files.
- Do not add links or signatures unless already present.
- Execute the Gmail action exactly once.
""",

        messages=[
            {
                "role": "user",
                "content": f"""
TO:
{to_email}

SUBJECT:
{subject}

BODY:
{body}

Execute the approved Gmail action now.
"""
            }
        ],
    )


    # -----------------------------------------------------
    # CHECK RESULT
    # -----------------------------------------------------

    tool_calls = []

    success = False


    for block in response.content:

        block_type = getattr(
            block,
            "type",
            None,
        )


        if block_type == "mcp_tool_use":

            tool_name = getattr(
                block,
                "name",
                "",
            )

            tool_calls.append(
                tool_name
            )


        elif block_type == "mcp_tool_result":

            if getattr(
                block,
                "is_error",
                False,
            ):

                errors = []

                for item in block.content:

                    if hasattr(
                        item,
                        "text",
                    ):
                        errors.append(
                            item.text
                        )


                raise ValueError(
                    "Zapier MCP Gmail error: "
                    + "\n".join(errors)
                )


            success = True


    # -----------------------------------------------------
    # MAKE SURE TOOL WAS CALLED
    # -----------------------------------------------------

    if not tool_calls:

        raise ValueError(
            "Claude did not call a Gmail tool."
        )


    correct_tool = False


    for tool_name in tool_calls:

        lower_name = (
            tool_name.lower()
        )

        if all(
            word in lower_name
            for word in expected_words
        ):

            correct_tool = True

            break


    if not correct_tool:

        raise ValueError(
            "Unexpected MCP tool used: "
            + ", ".join(tool_calls)
        )


    if not success:

        raise ValueError(
            "Gmail tool ran but no successful "
            "result was returned."
        )


    return True


# ---------------------------------------------------------
# CREATE DRAFT
# ---------------------------------------------------------

def create_gmail_draft(
    to_email: str,
    subject: str,
    body: str,
):

    return _execute_gmail_action(
        action="draft",
        to_email=to_email,
        subject=subject,
        body=body,
    )


# ---------------------------------------------------------
# SEND EMAIL
# ---------------------------------------------------------

def send_gmail_email(
    to_email: str,
    subject: str,
    body: str,
):

    return _execute_gmail_action(
        action="send",
        to_email=to_email,
        subject=subject,
        body=body,
    )