from django.shortcuts import render
from main.models import Experience, Education, TechStack

def show_main(request):
    context = {
        "name": "Fairus",
        "full_name": "Muhammad Fairus Azfar Arisandi",
        "npm": "2506588752",
        "study_program": "S1 Sistem Informasi",
        "bio": "Undergraduate Information System Student at Universitas Indonesia",
        "education_list": Education.objects.all(),
        "techstack_list": TechStack.objects.all(),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Fairus",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)