class AIProviderConfigurationError(RuntimeError):
    """Raised when an AI provider cannot be configured safely."""


class AIProviderError(RuntimeError):
    """Raised when an AI provider request cannot be completed."""
