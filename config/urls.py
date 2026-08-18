from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='products:product_list'), name='home'),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('social/', include('allauth.urls')),
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
