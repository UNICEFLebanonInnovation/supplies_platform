from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^visits/$',
        view=views.TPMListView.as_view(),
        name='visits'
    ),
]
