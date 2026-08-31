class MatrixIdentityConflictError(Exception):
    """A Matrix ID is already verified for another local account."""


class MatrixIdentityError(Exception):
    """The MAS access token could not be resolved by the homeserver."""


class MatrixProfileError(Exception):
    """The Matrix profile could not be retrieved from the homeserver."""


class TokenEncryptionError(Exception):
    """A Matrix OAuth token could not be encrypted or decrypted."""


class MatrixOAuthTokenError(Exception):
    """A Matrix OAuth token could not be refreshed."""


class MatrixMediaError(Exception):
    """A Matrix media request could not be completed."""


class MatrixAvatarUnavailableError(Exception):
    """The requested user has no avatar this deployment can serve."""


class MatrixAvatarConfigurationError(Exception):
    """The deployment is not configured to proxy Matrix media."""


class LabelNotFoundError(Exception):
    pass


class ProjectTypeNotFoundError(Exception):
    pass


class ProjectLinkRequiredError(Exception):
    pass
