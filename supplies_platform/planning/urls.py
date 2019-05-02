from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^export-supply-goods/$',
        view=views.ExportSupplyGoodsViewSet.as_view(),
        name='export_supply_goods'
    ),
    url(
        regex=r'^export-supply-services/$',
        view=views.ExportSupplyServicesViewSet.as_view(),
        name='export_supply_services'
    ),
]
