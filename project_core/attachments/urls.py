
from django.urls import include, path

app_name = 'attachments'

urlpatterns = [
    path('api/v1/', include('attachments.api.v1.urls')), 
]