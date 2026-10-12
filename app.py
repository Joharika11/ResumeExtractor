
import json
import os

import streamlit as st
from dotenv import load_dotenv

from extractor import extract_resume, ResumeExtractionError
from parser import extract_text


load_dotenv()

st.set_page_config(
    page_title="Resume Extractor",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Resume Extractor")
st.write(
    "Upload a resume and convert it into structured, "
    "validated JSON using Gemini and Pydantic."
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "GEMINI_API_KEY is missing. Add it to your .env file "
        "and restart Streamlit."
    )
    st.stop()

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX.",
)

if uploaded_file is not None:
    st.caption(
        f"Selected file: {uploaded_file.name} "
        f"({uploaded_file.size / 1024:.1f} KB)"
    )

    if st.button("Extract resume information", type="primary"):
        if uploaded_file.size == 0:
            st.error("The uploaded file is empty.")
            st.stop()

        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("Please upload a file smaller than 10 MB.")
            st.stop()

        try:
            with st.spinner("Reading your resume..."):
                resume_text = extract_text(
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                )

            with st.spinner("Extracting and validating information..."):
                resume = extract_resume(resume_text, api_key)

            # Store only the validated result for display/download.
            result = resume.model_dump(mode="json")

            st.session_state["resume_result"] = result

            st.success("Resume extracted and validated successfully!")

        except ResumeExtractionError as error:
            st.error(str(error))

        except (ValueError, OSError) as error:
            st.error(f"Could not read the resume: {error}")

        except Exception:
            st.error(
                "An unexpected error occurred while processing "
                "the resume. Please try again."
            )

if "resume_result" in st.session_state:
    result = st.session_state["resume_result"]

    st.divider()
    st.subheader("Extracted information")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("**Candidate**")
        st.write(result.get("name") or "Not provided")

        st.markdown("**Email**")
        st.write(result.get("email") or "Not provided")

        st.markdown("**Phone**")
        st.write(result.get("phone") or "Not provided")

        st.markdown("**Location**")
        st.write(result.get("location") or "Not provided")

        st.markdown("**Years of experience**")
        experience = result.get("years_experience")
        st.write(experience if experience is not None else "Not provided")

    with right:
        st.markdown("**Skills**")
        skills = result.get("skills", [])

        if skills:
            st.write(", ".join(skills))
        else:
            st.write("No skills extracted")

        st.markdown("**Education**")
        st.json(result.get("education", []))

        st.markdown("**Work experience**")
        st.json(result.get("experience", []))

        st.markdown("**Projects**")
        st.json(result.get("projects", []))

    st.subheader("Validated JSON")
    json_output = json.dumps(result, indent=2, ensure_ascii=False)

    st.code(json_output, language="json")

    st.download_button(
        label="Download JSON",
        data=json_output,
        file_name="extracted_resume.json",
        mime="application/json",
    )

    if st.button("Clear extracted result"):
        del st.session_state["resume_result"]
        st.rerun()
