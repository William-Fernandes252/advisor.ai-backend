from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.papers.views import AuthorViewSet, PaperViewSet
from apps.users.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("papers", PaperViewSet)
router.register("authors", AuthorViewSet)


urlpatterns = router.urls
