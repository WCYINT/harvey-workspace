class BaseOrchestrator:
    def __init__(self, config: dict):
        self.config = config

    def run(self, action: str, payload: dict) -> dict:
        raise NotImplementedError
