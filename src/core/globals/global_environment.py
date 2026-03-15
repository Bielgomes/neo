from core.environment import Environment
from core.globals.time_counter import timeCounter


class GlobalEnvironment(Environment):
    def __init__(self, parent_environment: Environment | None = None) -> None:
        super().__init__(parent_environment)
        self.environment["timeCounter"] = timeCounter()
