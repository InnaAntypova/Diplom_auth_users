from django.urls import path
from users.apps import UsersConfig
from users.views import UserListAPIView, UserAuthAPIView, UserProfileUpdateDeleteAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name


urlpatterns = [
    path('login/', UserAuthAPIView.as_view(), name='login_user'),
    path('<int:pk>/', UserProfileUpdateDeleteAPIView.as_view(), name='user_profile_update_delete'),
    path('list/', UserListAPIView.as_view(), name='all_users_for_staff'),
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
