from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from products.views import japan_landing

from .views import serve_media

admin.site.site_header = 'dudu_outfits_store 管理'
admin.site.site_title = 'dudu_outfits_store 管理後台'
admin.site.index_title = '網站管理'

urlpatterns = [
    path('media/<path:path>', serve_media, name='media'),
    path('admin/', admin.site.urls),
    path('jp/', japan_landing, name='japan_landing'),
    path('', RedirectView.as_view(pattern_name='products:product_list'), name='home'),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('social/', include('allauth.urls')),
    path('', include('orders.urls')),
]
