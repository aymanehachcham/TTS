

from django.urls import path
from . import views
from django.conf import settings

from django.conf.urls.static import static


app_name = 'api'

urlpatterns = [
    path(r'test', views.test_api, name='test_api_communication'),
    path(r'run/', views.RetrieveAudios.as_view())

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)