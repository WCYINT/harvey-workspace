import json
import re
from typing import Any

from result_schema import (
    ResultValidationError,
    load_json_text,
    validate_analyze_result,
    validate_fix_result,
    validate_review_result,
    validate_write_result,
)


class ResultParseError(Exception):
    pass


JSON_BLOCK_RE = re.compile(r'```json\s*([\s\S]*?)```', re.IGNORECASE)


def extract_json_candidate(raw_text: str) -> str:
    raw_text = raw_text.strip()
    if raw_text.startswith('{') and raw_text.endswith('}'):
        return raw_text
    match = JSON_BLOCK_RE.search(raw_text)
    if match:
        return match.group(1).strip()
    raise ResultParseError('未找到 JSON 结果，请检查 prompt 或 fallback 逻辑')



def parse_json_result(raw_text: str, action: str) -> dict[str, Any]:
    candidate = extract_json_candidate(raw_text)
    try:
        data = load_json_text(candidate)
    except ResultValidationError as e:
        raise ResultParseError(str(e))

    try:
        if action == 'analyze':
            return validate_analyze_result(data)
        if action == 'write':
            return validate_write_result(data)
        if action == 'review':
            return validate_review_result(data)
        if action == 'fix':
            return validate_fix_result(data)
    except ResultValidationError as e:
        raise ResultParseError(str(e))

    raise ResultParseError(f'不支持的 action: {action}')
