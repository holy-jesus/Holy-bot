class BaseTrigger:
    type = ""

    def get(data: dict) -> dict | None:
        raise NotImplementedError()
