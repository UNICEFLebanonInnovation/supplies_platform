from django.conf.urls import url
from supplies_platform.drivers.views import DetailView

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.DriverListView.as_view(),
        name='drivers_list'
    ),
    # url(
    #     regex=r'^~redirect/$',
    #     view=views.UserRedirectView.as_view(),
    #     name='redirect'
    # ),
]
