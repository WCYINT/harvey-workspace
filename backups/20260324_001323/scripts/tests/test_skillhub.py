import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test skillhub auto-update parsing
from skillhub_auto_update import _parse_skillhub_output

def test_parse_slug_only():
    output = "hello-world  A cool skill  version: 1.0.0"
    result = _parse_skillhub_output(output, "clawhub")
    assert len(result) == 1
    assert result[0]["slug"] == "hello-world"

def test_parse_chinese_skip():
    output = "你好这个世界"
    result = _parse_skillhub_output(output, "skillhub")
    assert len(result) == 0

def test_parse_empty():
    assert _parse_skillhub_output("", "clawhub") == []
    assert _parse_skillhub_output("   ", "skillhub") == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])