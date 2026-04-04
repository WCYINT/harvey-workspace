from pathlib import Path


def build_openclaw_request(config: dict, action: str, payload: dict) -> dict:
    openclaw = config.get('openclaw', {})
    return {
        'runtime': 'subagent',
        'agent_id': openclaw.get('agent_id', ''),
        'mode': openclaw.get('mode', 'run'),
        'model': openclaw.get('model', ''),
        'timeout_seconds': openclaw.get('timeout_seconds', 900),
        'action': action,
        'payload': payload,
    }
