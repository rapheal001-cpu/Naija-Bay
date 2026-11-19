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
from NaijaBay.media_uploads import (
    upload_initiate_view,
    upload_part_url_view,
    upload_parts_list_view,
    upload_complete_view,
    upload_abort_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{API_VERSION}accounts/auth/', include('accounts.urls')),
    path(f'{API_VERSION}products/', include('products.urls')),
    path(f'{API_VERSION}core/', include('core.urls')),
    path(f'{API_VERSION}messaging/', include('messaging.urls')),
    path(f'{API_VERSION}orders/', include('orders.urls')),
    path(f'{API_VERSION}payments/', include('payments.urls')),
    path(f'{API_VERSION}storage/media/uploads/initiate/', upload_initiate_view, name='media-upload-initiate'),
    path(f'{API_VERSION}storage/media/uploads/part-url/', upload_part_url_view, name='media-upload-part-url'),
    path(f'{API_VERSION}storage/media/uploads/parts/', upload_parts_list_view, name='media-upload-parts'),
    path(f'{API_VERSION}storage/media/uploads/complete/', upload_complete_view, name='media-upload-complete'),
    path(f'{API_VERSION}storage/media/uploads/abort/', upload_abort_view, name='media-upload-abort'),
    path(f'{API_VERSION}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_VERSION}docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_VERSION}redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)