from django.urls import path
from .views import DocumentViewSet

urlpatterns = [
    path('summary/', DocumentViewSet.as_view({'get': 'list', 'post': 'create'}))
]
