class RequestError(BaseException):
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response

        super().__init__(status_code)
