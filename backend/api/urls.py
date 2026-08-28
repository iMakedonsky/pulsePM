from ninja import NinjaAPI

from .auth import router as auth_router

api = NinjaAPI(title='PulsePM API', version='1.0.0')
api.add_router('', auth_router)
