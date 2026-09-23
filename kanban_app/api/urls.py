from django.urls import path, include
from .views import BoardViewSet, TaskViewSet, EmailViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'email-check', EmailViewSet, basename='email-check')

urlpatterns = [
    path('', include(router.urls), name='boards_list'),
    path('', include(router.urls), name='tasks_list'),
    path('', include(router.urls), name='email-check'),
]