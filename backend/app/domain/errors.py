class ConversationNotFoundError(LookupError):
    pass


class ConversationSchemaMismatchError(ValueError):
    pass


class QuerySchemaNotFoundError(LookupError):
    pass


class QuerySchemaUnavailableError(ValueError):
    pass


class UserAlreadyExistsError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass
