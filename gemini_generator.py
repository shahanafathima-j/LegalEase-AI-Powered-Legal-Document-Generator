import os
from typing import Dict

from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Generate legal-document drafts with Gemini.

    The project documentation originally specified Gemini 1.5 Pro.
    The model is configurable so the application can use a currently
    available Gemini model without changing source code.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ).strip()

        self._client = None

        if (
            self.api_key
            and self.api_key != "your_gemini_api_key_here"
            and self.api_key != "YOUR_GEMINI_API_KEY_HERE"
        ):
            try:
                from google import genai

                self._client = genai.Client(
                    api_key=self.api_key
                )

            except Exception as exc:
                print(
                    "Gemini client initialization failed:",
                    repr(exc),
                )

                self._client = None

    @property
    def demo_mode(self) -> bool:
        return self._client is None

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str = "",
    ) -> Dict[str, str | bool]:

        # -------------------------------------------------
        # 1. Gemini client unavailable
        # -------------------------------------------------

        if self._client is None:

            print(
                "Gemini client unavailable. "
                "Using demo mode."
            )

            return {
                "content": self._demo_document(
                    document_type,
                    parties,
                    terms,
                    effective_date,
                    jurisdiction,
                ),
                "demo_mode": True,
                "model": "demo-mode",
            }

        # -------------------------------------------------
        # 2. Build Gemini prompt
        # -------------------------------------------------

        prompt = self._build_prompt(
            document_type,
            parties,
            terms,
            effective_date,
            jurisdiction,
        )

        # -------------------------------------------------
        # 3. Try Gemini generation
        # -------------------------------------------------

        try:

            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            content = (
                response.text
                if response.text
                else ""
            ).strip()

            if not content:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            print(
                f"Gemini generation successful "
                f"using {self.model}"
            )

            return {
                "content": content,
                "demo_mode": False,
                "model": self.model,
            }

        # -------------------------------------------------
        # 4. Gemini quota / API error
        # -------------------------------------------------

        except Exception as exc:

            error_text = str(exc)

            print(
                "Gemini generation error:",
                repr(exc),
            )

            # Gemini Free Tier / rate-limit / quota
            # errors should fall back to demo mode.

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "quota" in error_text.lower()
            ):

                print(
                    "Gemini quota exceeded. "
                    "Switching to demo mode."
                )

                return {
                    "content": self._demo_document(
                        document_type,
                        parties,
                        terms,
                        effective_date,
                        jurisdiction,
                    ),
                    "demo_mode": True,
                    "model": (
                        "demo-mode "
                        "(Gemini quota exceeded)"
                    ),
                }

            # Other errors should still be shown
            # so we can identify and fix them.

            raise

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:

        jurisdiction_text = (
            jurisdiction
            if jurisdiction
            else "Not specified"
        )

        return f"""
You are a professional legal-document drafting assistant.

Create a structured FIRST DRAFT of the requested legal document.

Do not claim that the document is legally valid,
enforceable, or reviewed by a lawyer.

Use clear formal language.

Preserve every user-provided fact and requested term.

Do not invent:

- names
- amounts
- dates
- addresses
- laws
- obligations

Where a necessary fact is missing,
use [TO BE COMPLETED] rather than guessing.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

JURISDICTION:
{jurisdiction_text}

Return the document using the following structure:

TITLE

INTRODUCTION

1. PARTIES

2. PURPOSE

3. DEFINITIONS

4. OBLIGATIONS

5. PAYMENT / CONSIDERATION

6. CONFIDENTIALITY

7. TERM AND TERMINATION

8. DISPUTE / GOVERNING LAW

9. GENERAL PROVISIONS

10. SIGNATURES

Adapt the sections to the document type.

Do not create unnecessary sections.

Use plain text headings.

Do not use markdown tables.

End with:

DRAFTING NOTICE

State that the document is an AI-generated draft,
has not been reviewed by a lawyer,
and should be reviewed by a qualified legal professional
before use.
""".strip()

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:

        # -------------------------------------------------
        # Convert user terms into numbered clauses
        # -------------------------------------------------

        term_items = [
            item.strip()
            for item in terms.split(";")
            if item.strip()
        ]

        if term_items:

            bullets = "\n".join(
                f"{index}. {item}"
                for index, item in enumerate(
                    term_items,
                    start=1,
                )
            )

        else:

            bullets = (
                "1. [TO BE COMPLETED]"
            )

        # -------------------------------------------------
        # Demo legal-document draft
        # -------------------------------------------------

        return f"""
{document_type.upper()}

EFFECTIVE DATE: {effective_date}


INTRODUCTION

This document is a first draft prepared from
the information supplied by the parties.


1. PARTIES

{parties}


2. PURPOSE

This document records the arrangement described
by the parties and is provided as a draft for
review and completion.


3. JURISDICTION

{jurisdiction or "[TO BE COMPLETED]"}


4. KEY TERMS AND CONDITIONS

{bullets}


5. OBLIGATIONS

Each party shall perform the responsibilities
and obligations agreed between the parties.

The parties should verify that all obligations
are accurately described before signing.


6. PAYMENT / CONSIDERATION

Payment or other consideration shall be as
specified in the agreed terms.

If payment details are not specified, the parties
should complete this section before use.


7. CONFIDENTIALITY

Any confidentiality obligations agreed by the
parties should be clearly documented and reviewed
before signing.


8. TERM AND TERMINATION

The parties should confirm the applicable term,
termination conditions, notice period, and any
related obligations before execution.


9. GENERAL PROVISIONS

The parties should verify all material obligations,
payment details, timelines, confidentiality
requirements, termination conditions, notices,
and applicable-law provisions before signing.


10. SIGNATURES


PARTY 1

Signature: ______________________________

Name: __________________________________

Date: __________________________________


PARTY 2

Signature: ______________________________

Name: __________________________________

Date: __________________________________


DRAFTING NOTICE

This AI-generated draft is for informational and
document-preparation purposes only.

It has not been reviewed by a lawyer and should
be reviewed by a qualified legal professional
before use.

The parties should verify the document against
applicable law and their actual circumstances
before signing.
""".strip()