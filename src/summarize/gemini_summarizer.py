# src/summarize/gemini_summarizer.py
import os
from typing import List, Dict

# Try to import the new Google GenAI package (streamlit cloud will install google-genai)
# The package exposes `genai` / `Client` depending on version: we try a couple of import styles.
GENAI_AVAILABLE = False
_client = None

try:
    # preferred modern import
    from genai import Client
    GENAI_AVAILABLE = True
except Exception:
    try:
        import google.genai as genai_mod  # older variations
        GENAI_AVAILABLE = True
    except Exception:
        GENAI_AVAILABLE = False

def _build_prompt(items: List[Dict]) -> str:
    lines = []
    for it in items:
        date = it.get("published") or "No date"
        headline = it.get("headline") or "No headline"
        summary = it.get("summary") or ""
        lines.append(f"- ({date}) {headline} — {summary}")
    prompt = (
        "You are a concise event summarizer. Given the list of article headlines and short summaries below, "
        "produce three outputs:\n\n1) A chronological timeline (date → event) with 1-2 lines per milestone.\n"
        "2) A short event summary (3-5 sentences).\n3) Key facts bullet list.\n\n"
        "OUTPUT in plain text with clear section headers: TIMELINE, SUMMARY, KEY FACTS.\n\n"
        "ARTICLES:\n" + "\n".join(lines) + "\n\n"
        "Provide the output now."
    )
    return prompt

def summarize_with_gemini(items: List[Dict]) -> str:
    """
    Use Gemini (google-genai) to generate the summary. If Gemini is not available or fails, return a fallback.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return _fallback_summary(items)

    prompt = _build_prompt(items)

    # Try to use genai.Client (newer API)
    try:
        from genai import Client
        client = Client(api_key=api_key)
        # generate: depending on genai version the call might be client.generate or client.predict/generate_text
        try:
            resp = client.generate(model="gemini-2.0-flash", input=prompt, max_output_tokens=512)
            # try common fields
            if hasattr(resp, "output_text"):
                text = resp.output_text
            elif hasattr(resp, "text"):
                text = resp.text
            else:
                text = str(resp)
            return text
        except Exception:
            # try another call shape
            resp = client.models.generate(model="gemini-2.0-flash", prompt=prompt, max_output_tokens=512)
            # try parsing
            text = getattr(resp, "text", None) or str(resp)
            return text
    except Exception:
        # Last effort: try google-genai v2 style import
        try:
            import google.genai as genai
            genai.configure(api_key=api_key)
            model = genai.Model("gemini-2.0-flash")
            response = model.generate_text(prompt)
            # try common access
            text = getattr(response, "text", None) or str(response)
            return text
        except Exception:
            return _fallback_summary(items)

def _fallback_summary(items: List[Dict]) -> str:
    # Simple fallback: list timeline items + short aggregate summary
    lines = []
    for it in items:
        date = it.get("published") or "No date"
        headline = it.get("headline") or "No headline"
        lines.append(f"- ({date}) {headline}")
    summary = " / ".join([it.get("headline","") for it in items[:5]])
    result = "TIMELINE\n" + "\n".join(lines) + "\n\n" + "SUMMARY\n" + summary + "\n\n" + "KEY FACTS\n- Facts are from source headlines."
    return result

# exported function
def summarize_timeline(items: List[Dict]) -> str:
    return summarize_with_gemini(items)
