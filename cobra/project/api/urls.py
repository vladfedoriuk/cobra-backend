from django.urls import path
from rest_framework.routers import DefaultRouter

from cobra.project.api.views.epic import EpicListViewSet, EpicUpdateRetrieveViewSet
from cobra.project.api.views.invitation import ProjectInvitationViewSet
from cobra.project.api.views.issue import IssueListViewSet, IssueUpdateRetrieveViewSet
from cobra.project.api.views.membership import ProjectMembershipViewSet
from cobra.project.api.views.project import ProjectViewSet, RetrieveProjectApiView

router = DefaultRouter()

app_name = "project"

router.register(r"projects", ProjectViewSet)
router.register(r"invitation", ProjectInvitationViewSet)
router.register(r"membership", ProjectMembershipViewSet)
router.register(r"epic", EpicUpdateRetrieveViewSet)
router.register(r"epic", EpicListViewSet)
router.register(r"issue", IssueUpdateRetrieveViewSet)
router.register(r"issue", IssueListViewSet)


urlpatterns = [
    path(
        "project/<str:username>/<slug:slug>/",
        RetrieveProjectApiView.as_view(),
        name="project-by-username-slug",
    ),
] + router.urls
