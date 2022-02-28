import json
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import *


def index(request):
    posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, "network/index.html", {
        'page_obj': page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You should be logged in."}, status=400)

    data = json.loads(request.body)

    post = data.get("post", "")
    if len(post) > 280 or len(post) < 1:
        return JsonResponse({"error": "Post can't have more than 280 characters or less than 1"}, status=400)

    user = request.user
    timestamp = timezone.now()

    newpost = Post(user = user, post = post, timestamp = timestamp, likes = 0)
    newpost.save()

    return JsonResponse({"message": "Post created successfully."}, status=201)

def get_followage(username):
    follows = Follow.objects.all()
    counter_followers = 0
    counter_following = 0
    for follow in follows:
        if follow.followers.username == username:
            counter_following += 1
        if follow.following.username == username:
            counter_followers += 1
    return counter_followers, counter_following
    
def get_profile(request, username):
    try:
        user = User.objects.get(username = username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User Not Found.'}, status = 404)
    posts = Post.objects.filter(user = user).order_by("-timestamp").all()
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    followers, following = get_followage(username)
    if (user == request.user):
        return render(request, "network/profile.html", {
            "user_profile": user,
            "owner": True,
            'page_obj': page_obj,
            "followers": followers,
            "following_number": following
        })
    try:
        if not request.user.is_authenticated:
            already_following = False
        else:
            Follow.objects.get(followers = request.user, following = user)
            already_following = True
    except Follow.DoesNotExist:
        already_following = False
    return render(request, "network/profile.html", {
        "user_profile": user,
        "following": already_following,
        'page_obj': page_obj,
        "followers": followers,
        "following_number": following
    })

@login_required
def follow_page(request):
    users = []
    following = Follow.objects.filter(followers = request.user)
    for follow in following:
        users.append(follow.following)
    posts = Post.objects.filter(user__in = users)
    posts = posts.order_by("-timestamp").all()
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

@login_required
@csrf_exempt
def follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)

    following = data.get("following", "")
    following = User.objects.get(username__iexact = following)

    request.user.follow(following)
    return JsonResponse({"message": "Follow created successfully."}, status=201)

@login_required
@csrf_exempt
def unfollow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)

    following = data.get("following", "")
    following = User.objects.get(username__iexact = following)

    request.user.unfollow(following)
    return JsonResponse({"message": "Follow deleted successfully."}, status=201)

@login_required
@csrf_exempt
def update_post(request, post_id):
    try:
        post = Post.objects.get(id = post_id, user = request.user)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    data = json.loads(request.body)
    post_content = data.get("post", "")
    if len(post_content.strip()) > 280 or len(post_content.strip()) < 1:
        return JsonResponse({"error": "Post can't have more than 280 characters or less than 1"}, status=400)
    else:
        post.post = post_content
        post.save()
        return JsonResponse({"message": "Email updated successfully."}, status=201)

@login_required
@csrf_exempt
def like(request, post_id):
    try:
        post = Post.objects.get(id = post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    like = data.get("like")
    if like:
        Like.objects.create(liker = request.user, post = post)
        like_count = Like.objects.filter(post = post).count()
    else: 
        Like.objects.filter(liker = request.user, post = post).delete()
        like_count = Like.objects.filter(post = post).count()
    post.likes = like_count
    post.save()
    return JsonResponse({"message": "Email updated successfully."}, status=201)