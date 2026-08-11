from django.contrib import admin
from django.urls import (
    path,
    include
)
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from NaijaBay.utils import API_VERSION


urlpatterns = [
    # Admin urls
    path(f'{API_VERSION}admin/', admin.site.urls),
    # Accounts urls
    path(f'{API_VERSION}accounts/auth/', include('accounts.urls')),
    # Products urls
    path(f'{API_VERSION}products/', include('products.urls')),
    # Core urls
    path(f'{API_VERSION}core/', include('core.urls')),
    # Drf spectacular urls
    path(f'{API_VERSION}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_VERSION}docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_VERSION}redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)