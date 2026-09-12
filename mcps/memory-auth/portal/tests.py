import base64

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MemorySpace, PersonalAccessToken, Project


@override_settings(PAT_PEPPER="test-pepper", INTROSPECTION_SECRET="test-secret")
class PersonalAccessTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="test-password")
        self.space = MemorySpace.objects.create(owner=self.user, name="Работа")

    def issue(self, **overrides):
        values = {
            "user": self.user,
            "name": "Codex",
            "scope_type": PersonalAccessToken.ScopeType.SPACE,
            "project": None,
            "memory_space": self.space,
            "can_read": True,
            "can_write": True,
        }
        values.update(overrides)
        return PersonalAccessToken.issue(**values)

    def test_raw_token_is_not_stored_and_can_be_revoked(self):
        token, raw = self.issue()
        self.assertNotIn(raw, token.secret_digest)
        self.assertEqual(PersonalAccessToken.authenticate(raw), token)
        token.revoke()
        self.assertIsNone(PersonalAccessToken.authenticate(raw))

    def test_project_token_stops_working_after_membership_removal(self):
        project = Project.objects.create(slug="alpha", name="Alpha")
        project.members.add(self.user)
        _, raw = self.issue(
            scope_type=PersonalAccessToken.ScopeType.PROJECT,
            project=project,
            memory_space=None,
        )
        self.assertIsNotNone(PersonalAccessToken.authenticate(raw))
        project.members.remove(self.user)
        self.assertIsNone(PersonalAccessToken.authenticate(raw))

    def test_introspection_returns_namespace_scopes(self):
        token, raw = self.issue()
        credentials = base64.b64encode(b"qdrant-mcp:test-secret").decode()
        response = self.client.post(
            reverse("introspect"),
            {"token": raw},
            HTTP_AUTHORIZATION=f"Basic {credentials}",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["active"])
        self.assertEqual(body["client_id"], str(token.id))
        self.assertIn(f"memory:namespace:space:{self.space.id}", body["scope"])
        self.assertIn("memory:write", body["scope"])

    def test_two_spaces_have_different_namespaces(self):
        second_space = MemorySpace.objects.create(owner=self.user, name="Личное")
        first_token, _ = self.issue(name="Первое")
        second_token, _ = self.issue(name="Второе", memory_space=second_space)
        self.assertNotEqual(first_token.namespace_id, second_token.namespace_id)

    def test_introspection_rejects_wrong_service_secret(self):
        _, raw = self.issue()
        credentials = base64.b64encode(b"qdrant-mcp:wrong").decode()
        response = self.client.post(
            reverse("introspect"),
            {"token": raw},
            HTTP_AUTHORIZATION=f"Basic {credentials}",
        )
        self.assertEqual(response.status_code, 403)
