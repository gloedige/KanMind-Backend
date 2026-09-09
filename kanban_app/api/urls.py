from django.urls import path
from .views import BoardsListView

urlpatterns = [
    path('', BoardsListView.as_view(), name='boards_list')
]