class MatrixIdentityConflictError(Exception):
    """A Matrix ID is already verified for another local account."""


class MatrixIdentityError(Exception):
    """The MAS access token could not be resolved by the homeserver."""


class MatrixProfileError(Exception):
    """The Matrix profile could not be retrieved from the homeserver."""


class LabelNotFoundError(Exception):
    pass


class ProjectTypeNotFoundError(Exception):
    pass


class ProjectLinkRequiredError(Exception):
    pass
