
import json

from google import genai
from pydantic import ValidationError

from schemas import Resume


MODEL_NAME = "gemini-2.5-flash"
MAX_ATTEMPTS = 3


class ResumeExtractionError(Exception):
    """Raised when a resume cannot be extracted successfully."""


def extract_resume(resume_text: str, api_key: str) -> Resume:
    """Extract a resume into validated Pydantic data."""

    client = genai.Client(api_key=api_key)

    prompt = """
You are a resume information extraction system.

Extract information only from the supplied resume text.
Do not invent missing information.
Use null for unknown scalar fields and [] for unknown lists.
Preserve the meaning of the candidate's experience and projects.
Return a single JSON object, without Markdown code fences.

Required JSON structure:
{
  "name": null,
  "email": null,
  "phone": null,
  "location": null,
  "summary": null,
  "skills": [],
  "education": [],
  "experience": [],
  "projects": [],
  "years_experience": null,
  "certifications": [],
  "links": []
}

Each education item must contain:
institution, degree, field_of_study, graduation_year.

Each experience item must contain:
company, role, start_date, end_date, description.

Each project item must contain:
name, description, technologies.

For years_experience, use a non-negative number when it can
reasonably be determined from the resume. Otherwise use null.

Resume text:
<resume>
""" + resume_text + """
</resume>
"""

    feedback = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        current_prompt = prompt

        if feedback:
            current_prompt += f"""

Your previous response failed validation.

Correct the following issues:
{feedback}

Return the complete corrected JSON object.
Do not omit required schema fields.
Do not invent information to fix validation errors.
"""

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=current_prompt,
                config={
                    "response_mime_type": "application/json",
                },
            )

            raw_output = response.text

            if not raw_output:
                raise ValueError("Gemini returned an empty response.")

            # Step 1: Validate JSON syntax.
            data = json.loads(raw_output)

            # Step 2: Validate structure and field constraints.
            resume = Resume.model_validate(data)

            return resume

        except json.JSONDecodeError as error:
            feedback = (
                f"Invalid JSON: {error.msg}, "
                f"at line {error.lineno}, column {error.colno}."
            )

        except ValidationError as error:
            # Include field names and validation messages, not
            # the complete resume or candidate's personal data.
            feedback = json.dumps(
                [
                    {
                        "field": ".".join(str(part) for part in item["loc"]),
                        "error": item["msg"],
                        "type": item["type"],
                    }
                    for item in error.errors()
                ],
                indent=2,
            )

        except ValueError as error:
            feedback = str(error)

        except Exception as error:
            # API/network failures are not schema errors.
            # Don't waste validation retries on them.
            raise ResumeExtractionError(
                f"Gemini request failed: {type(error).__name__}"
            ) from error

        if attempt < MAX_ATTEMPTS:
            print(
                f"Validation attempt {attempt} failed. "
                f"Retrying ({attempt + 1}/{MAX_ATTEMPTS})..."
            )

    raise ResumeExtractionError(
        f"Could not produce a valid resume after "
        f"{MAX_ATTEMPTS} attempts. Last error: {feedback}"
    )
