from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_project,
    create_project,
    update_project,
    get_projects_json,
    delete_project,
    create_experience,
    update_experience,
    get_experience_json,
    delete_experience,
    register,
    login_user,
    logout_user,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="edit_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("api/experiences/", get_experience_json, name="get_experience_json"),
    path("project/", show_project, name="show_project"),
    path("project/add/", create_project, name="create_project"),
    path("project/<uuid:project_id>/edit/", update_project, name="edit_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]