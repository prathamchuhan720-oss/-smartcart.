"""
SmartCart URL Configuration.

Root URL dispatcher. All API endpoints are prefixed with /api/.
Swagger/ReDoc documentation available at /api/docs/ and /api/redoc/.
Single Page Application served at root `/`.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from core.views import SmartCartAppView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),

    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/wishlist/', include('wishlist.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/coupons/', include('coupons.urls')),
    path('api/admin/', include('analytics.urls')),
    path('api/notifications/', include('notifications.urls')),

    # Frontend SPA Entrypoint for all customer and admin dashboard routes
    path('', SmartCartAppView.as_view(), name='app-home'),
    re_path(r'^(?!api|admin|static|media).*$', SmartCartAppView.as_view(), name='app-spa'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass

admin.site.site_header = 'SmartCart Administration'
admin.site.site_title = 'SmartCart Admin'
admin.site.index_title = 'Dashboard'
