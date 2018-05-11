from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView,RedirectView
from django.views import defaults as default_views
from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view

from supplies_platform.locations.views import LocationAutocomplete
from supplies_platform.tpm.views import TPMVisitViewSet

api = routers.SimpleRouter()
api.register(r'tpm-visits', TPMVisitViewSet, base_name='tpm-visits')

schema_view = get_swagger_view(title='SMS API')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('supplies_platform.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^location-autocomplete/$', LocationAutocomplete.as_view(), name='location_autocomplete'),
    url(r'^tpm/', include('supplies_platform.tpm.urls', namespace='tpm')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', schema_view),

    url(r'^api/', include(api.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
