from django.urls import path, include
from .views import BoardViewSet, TaskViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls), name='boards_list'),
    path('', include(router.urls), name='tasks_list'),
]