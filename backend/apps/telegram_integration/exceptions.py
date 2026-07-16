class TelegramConfigurationError(RuntimeError):
    """Raised when the selected Telegram provider is not safely configured."""


class TelegramProviderError(RuntimeError):
    """Raised when a Telegram provider request cannot be completed."""


class TelegramUpdateProcessingError(RuntimeError):
    """Raised after a failed Telegram update is safely persisted."""
