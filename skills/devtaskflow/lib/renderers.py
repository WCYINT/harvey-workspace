from pathlib import Path


def render_review_summary(raw_text: str) -> dict:
    return {
        'format': 'markdown',
        'raw_text': raw_text,
    }


def render_plan_summary(plan_markdown: str) -> dict:
    return {
        'format': 'markdown',
        'raw_text': plan_markdown,
    }
