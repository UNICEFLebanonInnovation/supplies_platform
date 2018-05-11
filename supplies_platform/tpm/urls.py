from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^visits/$',
        view=views.TPMListView.as_view(),
        name='visits'
    ),
    url(
        regex=r'^assessment/(?P<pk>[\w.@+-]+)/$',
        view=views.TPMAssessment.as_view(),
        name='assessment'
    ),
    url(
        regex=r'^assessment/submission/$',
        view=views.TPMVisitSubmission.as_view(),
        name='submission'
    ),
]
