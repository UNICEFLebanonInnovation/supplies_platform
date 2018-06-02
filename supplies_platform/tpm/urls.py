from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^unicef-visits/$',
        view=views.SMListView.as_view(),
        name='unicef_visits'
    ),
    url(
        regex=r'^tpm-visits/$',
        view=views.SMListView.as_view(),
        name='tpm_visits'
    ),
    url(
        regex=r'^assessment/(?P<pk>[\w.@+-]+)/$',
        view=views.SMAssessment.as_view(),
        name='assessment'
    ),
    url(
        regex=r'^assessment/submission/$',
        view=views.SMVisitSubmission.as_view(),
        name='submission'
    ),
]
