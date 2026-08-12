class WorkHubException(Exception):
    """Base exception for WorkHub services."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)