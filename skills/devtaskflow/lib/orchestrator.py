from orchestrators.local_llm import LocalLLMOrchestrator
from orchestrators.openclaw_subagent import OpenClawSubagentOrchestrator


class OrchestratorError(Exception):
    pass


def get_orchestrator(config: dict):
    adapters = config.get('adapters', {})
    mode = adapters.get('orchestration', 'local_llm')

    if mode in {'none', '', None}:
        mode = 'local_llm'

    if mode == 'local_llm':
        return LocalLLMOrchestrator(config)
    if mode == 'openclaw_subagent':
        return OpenClawSubagentOrchestrator(config)

    raise OrchestratorError(f'不支持的 orchestration 模式: {mode}')
