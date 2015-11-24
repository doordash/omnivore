class OmnivoreError(Exception):
    def __init__(self, error, status_code=None, headers=None):
        super(OmnivoreError, self).__init__(error)

        self.error = error
        self.status_code = status_code
        self.headers = headers

    def __unicode__(self):
        return self.error


class APIError(OmnivoreError):
    pass


class APIConnectionError(OmnivoreError):
    pass


class InvalidRequestError(OmnivoreError):
    pass


class AuthenticationError(OmnivoreError):
    pass
