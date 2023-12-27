# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserSignupView, UserLoginView,DeliveryRequestViewSet, DeliverySentFormViewSet

router = DefaultRouter()
router.register(r'delivery_requests', DeliveryRequestViewSet)
router.register(r'delivery_sent_forms', DeliverySentFormViewSet)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('api/', include(router.urls)),
]
