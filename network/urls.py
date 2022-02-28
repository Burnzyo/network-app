
from os import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.get_profile, name="profile"),
    path("following", views.follow_page, name="follow_view"),

    #API Routes
    path("newpost", views.post, name="make_new_post"),
    path("follow", views.follow, name="start_following"),
    path("unfollow", views.unfollow, name="stop_following"),
    path("update/<int:post_id>", views.update_post, name="update_post"),
    path("like/<int:post_id>", views.like, name="like")
]
