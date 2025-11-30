from django.urls import path
from .views import (
    HomeView,
    CloudAccountListView,
    CloudAccountCreateView,
    EnvironmentListView,
    EnvironmentCreateView,
    EnvironmentDetailView,
    EnvironmentDeployView,
    SecurityPanelView,
    AdminToolsView,
    IaCPanelView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("cloud-accounts/", CloudAccountListView.as_view(), name="cloudaccount_list"),
    path("cloud-accounts/new/", CloudAccountCreateView.as_view(), name="cloudaccount_new"),
    path("environments/", EnvironmentListView.as_view(), name="env_list"),
    path("environments/new/", EnvironmentCreateView.as_view(), name="env_new"),
    path("environments/<slug:slug>/", EnvironmentDetailView.as_view(), name="env_detail"),
    path("environments/<slug:slug>/deploy/", EnvironmentDeployView.as_view(), name="env_deploy"),
    path("security/", SecurityPanelView.as_view(), name="security_panel"),
    path("tools/", AdminToolsView.as_view(), name="admin_tools"),
    path("iac/", IaCPanelView.as_view(), name="iac_panel"),
]
