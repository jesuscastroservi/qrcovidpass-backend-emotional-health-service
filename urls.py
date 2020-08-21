from views import (
    ViewReady,
    ViewLive,
    ViewEmotionalHealth
)
from utils.ext import url


urlpatterns = [
    url(ViewEmotionalHealth, endpoint='/emotional_health'),
    url(ViewReady, endpoint='/ready'),
    url(ViewLive, endpoint='/live')
]
