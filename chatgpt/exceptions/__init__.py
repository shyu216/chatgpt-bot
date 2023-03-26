class PresetNotFoundException(ValueError): ...


class ConcurrentMessageException(Exception): ...


class BotTypeNotFoundException(Exception): ...


class NoAvailableBotException(Exception): ...


class BotOperationNotSupportedException(Exception): ...


class BotRatelimitException(Exception):
    estimated_at: str

    def __init__(self, estimated_at):
        self.estimated_at = estimated_at


class APIKeyNoFundsError(Exception): ...
