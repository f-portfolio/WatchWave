
from django.urls import include, path

app_name = 'channels'

urlpatterns = [
    path('api/v1/', include('channels.api.v1.urls')), 
]