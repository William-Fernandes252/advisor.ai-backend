from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.users.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


urlpatterns = router.urls
