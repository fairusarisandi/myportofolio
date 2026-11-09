import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        cls.visitor = User.objects.create_user(username="visitor", password="test-password")
        cls.experience = Experience.objects.create(
            title="Portfolio", description="My website", category="full-time",
            thumbnail="https://example.com/portfolio.png", started_at="2026-01-01",
        )
        cls.list_url = reverse("api:experience-list")
        cls.detail_url = reverse("api:experience-detail", args=[cls.experience.id])
        cls.star_url = reverse("api:experience-star", args=[cls.experience.id])
        cls.payload = {
            "title": "New experience", "description": "A useful app", "category": "internship",
            "thumbnail": "https://example.com/experience.png",
            "started_at": "2026-02-01", "ended_at": None,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertEqual(response.data[0]["title"], self.experience.title)
        self.assertEqual(response.data[0]["description"], self.experience.description)
        self.assertEqual(response.data[0]["thumbnail"], self.experience.thumbnail)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data, response.data[0])
        self.assertEqual(detail.data["category_display"], "Full-Time")
        self.assertTrue(detail.data["is_ongoing"])
        self.assertEqual(detail.data["started_at"], "2026-01-01")

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(Experience.objects.count(), 1)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.experience.refresh_from_db()
            self.assertEqual(self.experience.title, "Portfolio")
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
            self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"description": "<p> </p>"}, "description"),
            ({"category": "invalid"}, "category"),
            ({"started_at": "bad-date"}, "started_at"),
            ({"ended_at": "2026-01-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")
        self.assertEqual(self.experience.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["starred_by"], [self.visitor.id])
        self.assertEqual(response.data["starred_by_names"], self.visitor.username)
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)
        self.assertEqual(response.data["starred_by"], [])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.pk],
            "is_ongoing": False, "category_display": "forged",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertEqual(response.data["starred_by"], [])
        self.assertTrue(response.data["is_ongoing"])
        self.assertEqual(response.data["category_display"], "Internship")
        self.assertEqual(Experience.objects.get(pk=response.data["id"]).starred_by.count(), 0)

    def test_staff_cannot_update_experiences_without_editor_group(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Portfolio")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Edited"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited")
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_text_sanitization(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "title": "<b>Clean title</b>",
            "description": "<p>Clean description</p>",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        experience = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(experience.title, "Clean title")
        self.assertEqual(experience.description, "Clean description")

    def test_patch_date_validation_uses_existing_values(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"ended_at": "2025-12-31"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)
        self.experience.ended_at = "2026-06-01"
        self.experience.save()
        response = self.client.patch(self.detail_url, {"started_at": "2026-07-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.detail_url, {"ended_at": None}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_ongoing"])
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)

    def test_page_controls_match_each_role(self):
        for role in ("guest", "visitor", "editor", "owner"):
            with self.subTest(role=role):
                self.client.logout()
                if role == "editor":
                    self.visitor.groups.add(Group.objects.get_or_create(name="Editor")[0])
                if role != "guest":
                    self.client.force_login(self.owner if role == "owner" else self.visitor)
                page = self.client.get(reverse("main:show_experience"))
                self.assertContains(page, f'data-experience-endpoint="{self.list_url}"')
                self.assertContains(page, "js/experience.js")
                if role in ("editor", "owner"):
                    self.assertContains(page, 'id="experience-form-modal"')
                    self.assertContains(page, "data-experience-edit-button")
                else:
                    self.assertNotContains(page, 'id="experience-form-modal"')
                    self.assertNotContains(page, "data-experience-edit-button")
                if role == "owner":
                    self.assertContains(page, "data-experience-add-button")
                    self.assertContains(page, "data-experience-delete-trigger")
                else:
                    self.assertNotContains(page, "data-experience-add-button")
                    self.assertNotContains(page, "data-experience-delete-trigger")
                if role == "guest":
                    self.assertContains(page, "Login untuk star")
                else:
                    self.assertContains(page, "data-experience-star-form")
