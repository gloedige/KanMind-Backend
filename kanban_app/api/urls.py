from django.urls import path, include
from .views import BoardViewSet, TaskViewSet, EmailViewSet, CommentViewSet
from rest_framework import routers
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'email-check', EmailViewSet, basename='email-check')

tasks_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', CommentViewSet, basename='task-comments')

urlpatterns = [
    path('', include(router.urls), name='boards_list'),
    path('', include(router.urls), name='tasks_list'),
    path('', include(router.urls), name='email-check'),
    path('', include(tasks_router.urls), name='task-comments'),
]