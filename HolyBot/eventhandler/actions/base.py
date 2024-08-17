class BaseAction:
    type = ""
    value = ""

    @staticmethod
    async def execute(data: dict):
        raise NotImplementedError()
