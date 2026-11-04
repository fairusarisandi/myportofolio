import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project, TechStack


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff BEM Fasilkom UI",
            description="Project Management Staff",
            category="full-time",
            thumbnail="http://127.0.0.1:8000/static/img/fairus.jpg",
            started_at=datetime.date(2026, 6, 1),
        )

        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="S1 Sistem Informasi",
            started_at=datetime.date(2025, 8, 1),
            logo="http://127.0.0.1:8000/static/img/fairus.jpg",
        )

        self.techstack = TechStack.objects.create(
            name="Python",
            logo="http://127.0.0.1:8000/static/img/fairus.jpg",
        )

        self.project = Project.objects.create(
            name="Project Django",
            description="Project untuk belajar Django",
            thumbnail="http://127.0.0.1:8000/static/img/fairus.jpg",
        )

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Staff BEM Fasilkom UI")
        self.assertEqual(self.experience.category, "full-time")
        self.assertTrue(self.experience.is_ongoing)
        self.assertEqual(self.experience.started_at, datetime.date(2026, 6, 1))

        self.experience.ended_at = datetime.date(2026, 12, 1)
        self.experience.save()
        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(self.experience.ended_at, datetime.date(2026, 12, 1))

    def test_education_model(self):
        self.assertEqual(str(self.education), "Universitas Indonesia")
        self.assertTrue(self.education.is_ongoing)
        self.assertEqual(self.education.started_at, datetime.date(2025, 8, 1))

        self.education.ended_at = datetime.date(2029, 8, 1)
        self.education.save()
        self.assertFalse(self.education.is_ongoing)
        self.assertEqual(self.education.ended_at, datetime.date(2029, 8, 1))
    
    def test_techstack_model(self):
        self.assertEqual(str(self.techstack), "Python")

    def test_project_model(self):
        self.assertEqual(str(self.project), "Project Django")

    def test_toggle_star_project_returns_updated_json_state(self):
        user = get_user_model().objects.create_user(username="project-star-user", password="password")
        self.client.force_login(user)
        url = reverse("main:toggle_star_project", args=[self.project.pk])

        starred_response = self.client.post(url, HTTP_ACCEPT="application/json")

        self.assertEqual(starred_response.status_code, 200)
        self.assertEqual(starred_response["Content-Type"], "application/json")
        self.assertEqual(
            starred_response.json(),
            {
                "is_starred": True,
                "star_count": 1,
                "starred_by_names": "project-star-user",
            },
        )
        self.assertTrue(self.project.starred_by.filter(pk=user.pk).exists())

        unstarred_response = self.client.post(url, HTTP_ACCEPT="application/json")

        self.assertEqual(unstarred_response.status_code, 200)
        self.assertEqual(
            unstarred_response.json(),
            {
                "is_starred": False,
                "star_count": 0,
                "starred_by_names": "",
            },
        )
        self.assertFalse(self.project.starred_by.filter(pk=user.pk).exists())

    def test_toggle_star_project_requires_post(self):
        user = get_user_model().objects.create_user(username="project-star-user", password="password")
        self.client.force_login(user)

        response = self.client.get(reverse("main:toggle_star_project", args=[self.project.pk]))

        self.assertEqual(response.status_code, 405)

    def test_update_project_ajax_updates_project_for_editor(self):
        user = get_user_model().objects.create_user(username="project-editor", password="password")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        user.groups.add(editor_group)
        self.client.force_login(user)

        response = self.client.post(
            reverse("main:update_project_ajax", args=[self.project.pk]),
            {
                "name": "Updated project",
                "description": "Updated description",
                "thumbnail": "https://example.com/updated.png",
            },
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Proyek berhasil diperbarui.", "pk": str(self.project.pk)})
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated project")
        self.assertEqual(self.project.description, "Updated description")
        self.assertEqual(self.project.thumbnail, "https://example.com/updated.png")

    def test_update_project_ajax_rejects_non_editors(self):
        user = get_user_model().objects.create_user(username="project-viewer", password="password")
        self.client.force_login(user)

        response = self.client.post(
            reverse("main:update_project_ajax", args=[self.project.pk]),
            {
                "name": "Updated project",
                "description": "Updated description",
                "thumbnail": "",
            },
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json().get("pk"))

    def test_editor_project_page_renders_edit_modal(self):
        user = get_user_model().objects.create_user(username="project-editor", password="password")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        user.groups.add(editor_group)
        self.client.force_login(user)

        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="project-form-modal"')
        self.assertContains(response, "data-project-edit-button")
        self.assertNotContains(response, "data-project-add-button")

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Fairus")
        self.assertContains(response, "Muhammad Fairus Azfar Arisandi")
        self.assertContains(response, "2506588752")
        self.assertContains(response, "S1 Sistem Informasi")
        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.degree)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_project")}"')

    def test_main_empty_education_and_techstack(self):
        Education.objects.all().delete()
        TechStack.objects.all().delete()
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No education information available.")
        self.assertContains(response, "No tech stack information available.")

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, 'id="experience-card-template"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, f'data-experience-endpoint="{reverse("main:get_experience_json")}"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_project")}"')

        data_response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(data_response.status_code, 200)
        data = data_response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.experience.pk))
        fields = data[0]["fields"]
        self.assertEqual(fields["title"], self.experience.title)
        self.assertEqual(fields["description"], self.experience.description)
        self.assertEqual(fields["category_display"], "Full-Time")
        self.assertIsNone(fields["ended_at"])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.localdate()
        self.experience.save()
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.experience.is_ongoing)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.experience.pk))
        self.assertEqual(data[0]["fields"]["ended_at"], self.experience.ended_at.isoformat())

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, "Belum ada experience yang ditambahkan atau ditemukan.")
        data_response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(data_response.status_code, 200)
        self.assertEqual(data_response.json(), [])

    def test_project_page(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, 'id="project-card-template"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, f'data-projects-endpoint="{reverse("api:project-list")}"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

        data_response = self.client.get(reverse("api:project-list"))
        self.assertEqual(data_response.status_code, 200)
        data = data_response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(self.project.pk))
        self.assertEqual(data[0]["name"], self.project.name)
        self.assertEqual(data[0]["description"], self.project.description)
        self.assertEqual(data[0]["thumbnail"], self.project.thumbnail)

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, "Belum ada proyek yang ditambahkan atau ditemukan.")
        data_response = self.client.get(reverse("api:project-list"))
        self.assertEqual(data_response.status_code, 200)
        self.assertEqual(data_response.json(), [])

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)
