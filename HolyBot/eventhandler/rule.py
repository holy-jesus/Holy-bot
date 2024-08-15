from trigger import Trigger
from action import Action

class Rule:
    def __init__(self, trigger: Trigger, action: Action) -> None:
        self.trigger = trigger
        self.action = action

    def __call__(self, *args, **kwds):
        pass
