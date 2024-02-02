from django.test.client import Client
from django.urls import reverse

from web.models import TechGroup
import pytest


@pytest.mark.django_db
def test_list_tech_groups(client: Client):
    # Arrange
    tech_group = TechGroup(
        name="List Tech Groups Test",
        description="List Tech Groups Test",
        enabled=True,
        homepage="https://spokanetech.org/",
    )
    tech_group.save()

    # Act
    url = reverse("web:list_tech_groups")
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.context["groups"].get().pk == tech_group.pk


@pytest.mark.django_db
def test_get_tech_group(client: Client):
    ...
