from django.urls import path, include
from .views import BoardsListViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'boards', BoardsListViewSet, basename='boards')

urlpatterns = [
    path('', include(router.urls), name='boards_list')
]