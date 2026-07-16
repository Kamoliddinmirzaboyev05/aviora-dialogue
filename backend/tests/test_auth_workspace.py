import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.workspaces.models import Workspace, WorkspaceMembership


pytestmark = pytest.mark.django_db


def test_demo_owner_can_login_and_see_workspace():
    user = get_user_model().objects.create_user(
        email="owner@example.com",
        password="ChangeMe123!",
        full_name="Demo Owner",
    )
    workspace = Workspace.objects.create(name="Demo Workspace", business_name="Demo CRM")
    WorkspaceMembership.objects.create(user=user, workspace=workspace, role=WorkspaceMembership.Role.OWNER)

    client = APIClient()
    login = client.post("/api/v1/auth/login/", {"email": "owner@example.com", "password": "ChangeMe123!"})

    assert login.status_code == 200
    assert login.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = client.get("/api/v1/auth/me/")
    workspaces = client.get("/api/v1/workspaces/")

    assert me.status_code == 200
    assert me.data["user"]["email"] == "owner@example.com"
    assert workspaces.status_code == 200
    assert workspaces.data["results"][0]["name"] == "Demo Workspace"


def test_workspace_list_only_returns_memberships():
    user = get_user_model().objects.create_user(email="owner@example.com", password="ChangeMe123!")
    visible = Workspace.objects.create(name="Visible", business_name="Visible Co")
    hidden = Workspace.objects.create(name="Hidden", business_name="Hidden Co")
    WorkspaceMembership.objects.create(user=user, workspace=visible, role=WorkspaceMembership.Role.OWNER)

    client = APIClient()
    login = client.post("/api/v1/auth/login/", {"email": "owner@example.com", "password": "ChangeMe123!"})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    response = client.get("/api/v1/workspaces/")

    names = {item["name"] for item in response.data["results"]}
    assert names == {"Visible"}
    assert hidden.name not in names
