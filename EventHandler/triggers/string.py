from enum import Enum


class Check(Enum):
    equal = "equals"
    contains = "contains"
    starts_with = "starts_with"
    ends_with = "ends_with"
    


class String:
    def __init__(self) -> None:
        pass

    def __eq__(self, other) -> bool:
        pass

    def verify_scheme(self):
        pass

    def check_rule(self):
        pass
