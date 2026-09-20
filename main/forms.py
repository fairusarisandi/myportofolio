from django.forms import DateInput, ModelForm, Select, TextInput, Textarea, URLInput
from main.models import Project, Experience

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "thumbnail",
        ]

        labels = {
            "name": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "thumbnail": "Thumbnail Proyek",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Deskripsi Proyek",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Judul Experience",
            "description": "Deskripsi Experience",
            "category": "Kategori Experience",
            "thumbnail": "Thumbnail Experience",
            "started_at": "Mulai Experience",
            "ended_at": "Selesai Experience",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Judul Experience",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Deskripsi Experience",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }