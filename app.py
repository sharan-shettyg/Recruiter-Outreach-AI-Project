import re
from urllib.parse import urlparse

import streamlit as st
from pypdf import PdfReader

from claude_client import generate_outreach
from hunter_mcp import find_recruiters

from zapier_mcp import (
    create_gmail_draft,
    send_gmail_email,
)


# =========================================================
# CONFIG
# =========================================================

MAX_BATCH_SIZE = 5


COUNTRIES = {
    "🇺🇸 United States": "US",
    "🇨🇦 Canada": "CA",
    "🇬🇧 United Kingdom": "GB",
    "🇮🇳 India": "IN",
    "🇦🇺 Australia": "AU",
    "🇩🇪 Germany": "DE",
    "🇸🇬 Singapore": "SG",
}


st.set_page_config(
    page_title="Recruiter Outreach AI",
    page_icon="🎯",
    layout="wide",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #fafafa;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #777;
        margin-bottom: 25px;
        font-size: 16px;
    }

    .recruiter-card {
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        background: white;
    }

    .verified {
        color: #16a34a;
        font-weight: 600;
    }

    .selected-count {
        font-size: 16px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎯 Recruiter Outreach AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Find recruiter emails → personalize cold outreach with Claude →
    review → create Gmail drafts or send directly.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Workflow")

    st.write("1️⃣ Enter company")
    st.write("2️⃣ Choose recruiter country")
    st.write("3️⃣ Enter target role")
    st.write("4️⃣ Upload your resume")
    st.write("5️⃣ Hunter finds recruiters")
    st.write("6️⃣ Select up to 5")
    st.write("7️⃣ Claude writes each email")
    st.write("8️⃣ Draft or send")

    st.divider()

    st.caption(
        "Each selected recruiter receives a separate "
        "personalized email."
    )

    st.caption(
        "Your resume is used only for Claude personalization. "
        "It is not attached to the email."
    )


# =========================================================
# HELPERS
# =========================================================

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    pages = []

    for page in reader.pages:

        text = page.extract_text() or ""

        pages.append(text)

    return "\n".join(pages).strip()


def normalize_domain(domain):

    domain = domain.strip().lower()

    if not domain:
        return ""

    if not domain.startswith(
        (
            "http://",
            "https://",
        )
    ):
        domain = "https://" + domain

    parsed = urlparse(domain)

    clean_domain = (
        parsed.netloc
        or parsed.path
    )

    clean_domain = (
        clean_domain
        .replace("www.", "")
        .strip("/")
    )

    return clean_domain


def valid_email(email):

    if not email:
        return False

    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email.strip(),
        )
    )


def recruiter_search_match(
    recruiter,
    query,
):

    if not query:
        return True

    query = query.lower().strip()

    searchable_text = " ".join(
        [
            recruiter.get("name", ""),
            recruiter.get("title", ""),
            recruiter.get("email", ""),
            recruiter.get("city", ""),
            recruiter.get("state", ""),
            recruiter.get("country", ""),
        ]
    ).lower()

    return query in searchable_text


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "recruiters": [],

    "selected_emails": [],

    "generated_emails": {},

    "sent_emails": set(),

    "drafted_emails": set(),
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# MAIN INPUT AREA
# =========================================================

input_left, input_right = st.columns(
    [1, 1],
    gap="large",
)


# =========================================================
# LEFT — SEARCH INPUTS
# =========================================================

with input_left:

    st.subheader(
        "🔎 Find Recruiters"
    )


    company = st.text_input(
        "Company",
        placeholder="e.g. Deloitte",
    )


    company_domain_input = st.text_input(
        "Company domain",
        placeholder="e.g. deloitte.com",
    )


    recruiter_country = st.selectbox(
        "Recruiter country",
        options=list(
            COUNTRIES.keys()
        ),
        index=0,
    )


    country_code = COUNTRIES[
        recruiter_country
    ]


    job_title = st.text_input(
        "Target role",
        placeholder="e.g. Technology Consultant",
    )


    resume_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
    )


    if resume_file is not None:

        st.success(
            f"✓ Resume uploaded: {resume_file.name}"
        )


    st.caption(
        "The resume helps Claude personalize your outreach. "
        "It will not be attached to the email."
    )


    # -----------------------------------------------------
    # FIND RECRUITERS
    # -----------------------------------------------------

    if st.button(
        "🔎 Find Recruiters",
        type="primary",
        use_container_width=True,
    ):

        clean_domain = normalize_domain(
            company_domain_input
        )


        if not clean_domain:

            st.error(
                "Enter a company domain."
            )


        else:

            try:

                with st.spinner(
                    f"Searching for recruiters in "
                    f"{recruiter_country}..."
                ):

                    recruiters = find_recruiters(
                        clean_domain,
                        country_code,
                    )


                # -----------------------------------------
                # REMOVE DUPLICATES / BAD EMAILS
                # -----------------------------------------

                unique_recruiters = {}


                for recruiter in recruiters:

                    email = (
                        recruiter
                        .get(
                            "email",
                            "",
                        )
                        .strip()
                        .lower()
                    )


                    if (
                        email
                        and valid_email(email)
                    ):

                        unique_recruiters[
                            email
                        ] = recruiter


                recruiters = list(
                    unique_recruiters.values()
                )


                st.session_state.recruiters = (
                    recruiters
                )


                st.session_state.selected_emails = []


                st.session_state.generated_emails = {}


                if recruiters:

                    st.success(
                        f"Found {len(recruiters)} "
                        f"recruiting contacts in "
                        f"{recruiter_country}."
                    )


                else:

                    st.warning(
                        "No matching recruiter contacts "
                        "were found."
                    )


            except Exception as error:

                st.error(
                    f"Recruiter search failed: {error}"
                )


# =========================================================
# RIGHT — SELECT RECRUITERS
# =========================================================

with input_right:

    st.subheader(
        "👥 Select Recruiters"
    )


    recruiters = (
        st.session_state.recruiters
    )


    if not recruiters:

        st.info(
            "Search for recruiters first."
        )


    else:

        recruiter_map = {

            recruiter["email"]:
            recruiter

            for recruiter
            in recruiters
        }


        recruiter_emails = list(
            recruiter_map.keys()
        )


        filter_query = st.text_input(
            "Filter results",
            placeholder=(
                "Search by recruiter name, "
                "title or email..."
            ),
        )


        filtered_emails = [

            email

            for email
            in recruiter_emails

            if recruiter_search_match(
                recruiter_map[email],
                filter_query,
            )
        ]


        selected_emails = st.multiselect(

            "Choose recruiters",

            options=filtered_emails,

            default=[
                email
                for email
                in st.session_state.selected_emails
                if email in filtered_emails
            ],

            format_func=lambda email: (
                f"{recruiter_map[email]['name']} "
                f"— "
                f"{recruiter_map[email]['title']} "
                f"— "
                f"{email}"
            ),
        )


        # ---------------------------------------------
        # LIMIT SELECTION
        # ---------------------------------------------

        if (
            len(selected_emails)
            > MAX_BATCH_SIZE
        ):

            st.warning(
                f"You can select a maximum of "
                f"{MAX_BATCH_SIZE} recruiters."
            )

            selected_emails = (
                selected_emails[
                    :MAX_BATCH_SIZE
                ]
            )


        st.session_state.selected_emails = (
            selected_emails
        )


        st.markdown(
            f"""
            <div class="selected-count">
            {len(selected_emails)}
            / {MAX_BATCH_SIZE}
            recruiters selected
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ---------------------------------------------
        # SELECTED RECRUITER CARDS
        # ---------------------------------------------

        for email in selected_emails:

            recruiter = (
                recruiter_map[email]
            )


            location_parts = [

                recruiter.get(
                    "city",
                    "",
                ),

                recruiter.get(
                    "state",
                    "",
                ),

                recruiter.get(
                    "country",
                    "",
                ),
            ]


            location = ", ".join(
                part
                for part
                in location_parts
                if part
            )


            st.markdown(
                f"""
                <div class="recruiter-card">

                <b>
                {recruiter.get('name', '')}
                </b>

                <br>

                {recruiter.get('title', '')}

                <br><br>

                📧 {recruiter.get('email', '')}

                <br>

                {
                    "📍 " + location + "<br>"
                    if location
                    else ""
                }

                <span class="verified">
                ✓ {recruiter.get('verification_status', 'valid')}
                </span>

                &nbsp; • &nbsp;

                Confidence:
                {recruiter.get('confidence', 0)}%

                </div>
                """,
                unsafe_allow_html=True,
            )


            if recruiter.get(
                "linkedin_url"
            ):

                st.link_button(
                    (
                        f"LinkedIn — "
                        f"{recruiter.get('name', '')}"
                    ),
                    recruiter[
                        "linkedin_url"
                    ],
                    use_container_width=True,
                )


# =========================================================
# GENERATE PERSONALIZED EMAILS
# =========================================================

st.divider()

st.subheader(
    "✨ Generate Personalized Emails"
)


if st.button(
    "Generate Emails for Selected Recruiters",
    type="primary",
    use_container_width=True,
):

    errors = []


    selected_emails = (
        st.session_state.selected_emails
    )


    if not selected_emails:

        errors.append(
            "Select at least one recruiter."
        )


    if (
        len(selected_emails)
        > MAX_BATCH_SIZE
    ):

        errors.append(
            f"Select no more than "
            f"{MAX_BATCH_SIZE} recruiters."
        )


    if not company.strip():

        errors.append(
            "Enter the company name."
        )


    if not job_title.strip():

        errors.append(
            "Enter your target role."
        )


    if resume_file is None:

        errors.append(
            "Upload your resume PDF."
        )


    if errors:

        for error in errors:

            st.error(error)


    else:

        try:

            # -----------------------------------------
            # EXTRACT RESUME
            # -----------------------------------------

            resume_text = extract_pdf_text(
                resume_file
            )


            if not resume_text:

                raise ValueError(
                    "Could not extract text "
                    "from the resume PDF."
                )


            recruiter_map = {

                recruiter["email"]:
                recruiter

                for recruiter
                in st.session_state.recruiters
            }


            generated = {}


            total = len(
                selected_emails
            )


            progress = st.progress(0)

            status = st.empty()


            # -----------------------------------------
            # ONE EMAIL PER RECRUITER
            # -----------------------------------------

            for index, email in enumerate(
                selected_emails,
                start=1,
            ):

                recruiter = (
                    recruiter_map[email]
                )


                status.write(
                    f"Generating email "
                    f"{index}/{total}: "
                    f"{recruiter['name']}"
                )


                # -------------------------------------
                # WE NO LONGER ASK THE USER FOR A JD.
                #
                # This context keeps the existing
                # claude_client.py compatible while
                # telling Claude this is cold outreach.
                # -------------------------------------

                outreach_context = (
                    f"The candidate is interested in "
                    f"{job_title} opportunities at "
                    f"{company}. "
                    f"This is general recruiter outreach "
                    f"and is not tied to a specific "
                    f"job posting."
                )


                result = generate_outreach(

                    resume_text=resume_text,

                    job_description=(
                        outreach_context
                    ),

                    recruiter_name=(
                        recruiter[
                            "name"
                        ]
                    ),

                    recruiter_email=(
                        recruiter[
                            "email"
                        ]
                    ),

                    company=company,

                    job_title=job_title,
                )


                generated[email] = {

                    "recruiter":
                    recruiter,

                    "result":
                    result,
                }


                st.session_state[
                    f"subject::{email}"
                ] = result[
                    "subject"
                ]


                st.session_state[
                    f"body::{email}"
                ] = result[
                    "body"
                ]


                progress.progress(
                    index / total
                )


            st.session_state.generated_emails = (
                generated
            )


            progress.empty()

            status.empty()


            st.success(
                f"Generated {total} "
                "personalized emails."
            )


        except Exception as error:

            st.error(
                f"Email generation failed: "
                f"{error}"
            )


# =========================================================
# REVIEW EMAILS
# =========================================================

generated_emails = (
    st.session_state.generated_emails
)


if generated_emails:

    st.divider()

    st.subheader(
        "📝 Review Emails"
    )


    st.caption(
        "Each recruiter receives a separate "
        "personalized email."
    )


    for email, data in (
        generated_emails.items()
    ):

        recruiter = (
            data[
                "recruiter"
            ]
        )


        result = (
            data[
                "result"
            ]
        )


        with st.expander(
            (
                f"{recruiter['name']} "
                f"— "
                f"{recruiter['title']} "
                f"— "
                f"{email}"
            ),
            expanded=True,
        ):


            # -----------------------------------------
            # OUTREACH ANGLE
            # -----------------------------------------

            strengths = (
                result.get(
                    "strengths",
                    [],
                )
            )


            if strengths:

                st.write(
                    "**Outreach angle:**"
                )


                for strength in strengths:

                    st.write(
                        f"• {strength}"
                    )


            # -----------------------------------------
            # SUBJECT
            # -----------------------------------------

            st.text_input(
                "Subject",
                key=f"subject::{email}",
            )


            # -----------------------------------------
            # EMAIL BODY
            # -----------------------------------------

            st.text_area(
                "Email",
                height=280,
                key=f"body::{email}",
            )


            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            if (
                email
                in st.session_state.sent_emails
            ):

                st.success(
                    "✓ Already sent during "
                    "this app session."
                )


            elif (
                email
                in st.session_state.drafted_emails
            ):

                st.info(
                    "✓ Gmail draft already created "
                    "during this session."
                )


# =========================================================
# DELIVERY
# =========================================================

if generated_emails:

    st.divider()

    st.subheader(
        "📤 Delivery"
    )


    st.info(
        "Your resume was used by Claude "
        "for personalization. "
        "It will not be attached."
    )


    approved = st.checkbox(
        (
            "I have reviewed the recipients, "
            "subjects, and email bodies."
        )
    )


    draft_col, send_col = (
        st.columns(2)
    )


    # -----------------------------------------------------
    # CREATE DRAFTS BUTTON
    # -----------------------------------------------------

    with draft_col:

        create_drafts_clicked = st.button(

            (
                f"📥 Create "
                f"{len(generated_emails)} Draft"
                f"{'s' if len(generated_emails) != 1 else ''}"
            ),

            use_container_width=True,

            disabled=not approved,
        )


    # -----------------------------------------------------
    # SEND EMAILS BUTTON
    # -----------------------------------------------------

    with send_col:

        send_clicked = st.button(

            (
                f"🚀 Send "
                f"{len(generated_emails)} Email"
                f"{'s' if len(generated_emails) != 1 else ''}"
            ),

            type="primary",

            use_container_width=True,

            disabled=not approved,
        )


    # =====================================================
    # CREATE DRAFTS
    # =====================================================

    if create_drafts_clicked:

        st.write(
            "### Creating Gmail Drafts"
        )


        for email, data in (
            generated_emails.items()
        ):

            recruiter = (
                data[
                    "recruiter"
                ]
            )


            subject = (
                st.session_state[
                    f"subject::{email}"
                ]
                .strip()
            )


            body = (
                st.session_state[
                    f"body::{email}"
                ]
                .strip()
            )


            if not subject:

                st.error(
                    f"{recruiter['name']}: "
                    "Subject is empty."
                )

                continue


            if not body:

                st.error(
                    f"{recruiter['name']}: "
                    "Email body is empty."
                )

                continue


            try:

                with st.spinner(
                    f"Creating draft for "
                    f"{recruiter['name']}..."
                ):

                    create_gmail_draft(

                        to_email=email,

                        subject=subject,

                        body=body,
                    )


                st.session_state.drafted_emails.add(
                    email
                )


                st.success(
                    f"✓ Draft created for "
                    f"{recruiter['name']} "
                    f"({email})"
                )


            except Exception as error:

                st.error(
                    f"✗ {recruiter['name']}: "
                    f"{error}"
                )


    # =====================================================
    # SEND EMAILS
    # =====================================================

    if send_clicked:

        st.warning(
            "Sending emails now. "
            "Each recruiter will receive "
            "a separate message."
        )


        st.write(
            "### Sending Emails"
        )


        for email, data in (
            generated_emails.items()
        ):

            recruiter = (
                data[
                    "recruiter"
                ]
            )


            # -----------------------------------------
            # PREVENT DUPLICATE SENDS
            # -----------------------------------------

            if (
                email
                in st.session_state.sent_emails
            ):

                st.warning(
                    f"Skipped "
                    f"{recruiter['name']} — "
                    "already sent during "
                    "this session."
                )

                continue


            subject = (
                st.session_state[
                    f"subject::{email}"
                ]
                .strip()
            )


            body = (
                st.session_state[
                    f"body::{email}"
                ]
                .strip()
            )


            if not subject:

                st.error(
                    f"{recruiter['name']}: "
                    "Subject is empty."
                )

                continue


            if not body:

                st.error(
                    f"{recruiter['name']}: "
                    "Email body is empty."
                )

                continue


            try:

                with st.spinner(
                    f"Sending to "
                    f"{recruiter['name']}..."
                ):

                    send_gmail_email(

                        to_email=email,

                        subject=subject,

                        body=body,
                    )


                st.session_state.sent_emails.add(
                    email
                )


                st.success(
                    f"✓ Sent to "
                    f"{recruiter['name']} "
                    f"({email})"
                )


            except Exception as error:

                st.error(
                    f"✗ {recruiter['name']}: "
                    f"{error}"
                )