from accounts.api.v1.views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


app_name = 'api-v1'

urlpatterns = [
    # registration
    path('registration/', RegistrationAPIView.as_view(), name='registration'),
    
    # verify registration
    path('confirm-registration/', ConfirmRegistrationView.as_view()), 
    
    # change password
    path('change-password/', ChangePasswordApiView.as_view(), name='change-password'),
    
    # reset password
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    
    # login token
    path('token/login/',CustomLoginView.as_view(), name='token-login'),
    path('token/logout/',CustomDiscardAuthToken.as_view(), name='token-logout'),

    # login jwt
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
    path('jwt/decode/', DecodeTokenView.as_view(), name='jwt-decode'),

    # profile
    path('profile/', ProfileApiView.as_view(), name='profile'),
    path('profile_edit_body/', ProfileEditBodyApiView.as_view(), name='profile-edit-body'),
    path('profile_edit_img/', ProfileEditImageApiView.as_view(), name='profile-edit-img'),
    
    # promotion
    path('request-promotion/', PromotionToStaffModelViewSet.as_view({'get':'list', 'post':'create'}), name='user-request-promotion'),
    path('request-promotion/<int:pk>/', PromotionToStaffModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name='user-request-promotion'),
    
]
