class MyResponse:
    def __init__(self, data: list[dict], response_status: int, errors: list[str] = None):
        self.data = data
        self.response_status = response_status
        if errors is None:
            self.errors = []

    def to_dict(self):
        return self.__dict__