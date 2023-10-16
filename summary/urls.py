from django.urls import path, include  # Import include to include the router URLs
from .views import DocumentViewSet, SummaryAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'summary-fetch', SummaryAPIView, basename='summary')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('summary/', DocumentViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'})),
]
