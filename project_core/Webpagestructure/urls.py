from django.urls import include, path

app_name = 'webpage'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path("api/v1/", include('webpage.api.v1.urls')),
]
