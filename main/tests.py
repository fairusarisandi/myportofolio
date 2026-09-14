import datetime
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
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Full-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_project")}"')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_project_page(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.description)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)