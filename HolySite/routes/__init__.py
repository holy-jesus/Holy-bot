from .auth import auth
from .profile import profile
from .api import api
# from .commands import commands
from .eventsub import eventsub

routes = (eventsub, auth, profile, api)