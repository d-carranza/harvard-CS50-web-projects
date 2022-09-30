import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django import forms
from django.db.models import F

from .models import Following, Like, Post, User

class NewPost(forms.Form):
    text = forms.CharField(max_length=140, label="Text", widget=forms.Textarea(attrs={"placeholder": "Share it with the world"}))

class EditPost(forms.Form):
    text = forms.CharField(max_length=140, label="Text", widget=forms.Textarea(attrs={"placeholder": "What did you want to say?"}))

# Main routes
def home(request): # Shows home

    # New Post
    if request.method == "POST":
        form = NewPost(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            #get current user object
            user = User.objects.get(pk=request.user.id)
            # create post
            newpost = Post(poster=user, text=text, likecount=0)
            # add newlisting to the database
            newpost.save()
            # redirects to home
            return HttpResponseRedirect(f"/home")

    # Pagination
    p = Paginator(Post.objects.all().order_by("-time"), 10)
    page = request.GET.get('page')
    posts = p.get_page(page)

    likeslist = []
    if request.user.is_authenticated:
        user = User.objects.get(username = request.user.username)
        likes = Like.objects.filter(user = user)
        for like in likes:
            likeslist.append(like.post.id)

    return render(request, "network/home.html", {
        "newpost": NewPost(),
        "editpost":EditPost(),
        "posts":posts,
        "likeslist": likeslist
    })

def profile(request, username):

    # User info
    auth = User.objects.filter(username = request.user.username).first()
    poster = User.objects.get(username = username)
    if auth != None:
        user = User.objects.get(username = request.user.username)

    else:
        user = None

    follows = Following.objects.all()
    followers = 0
    following = 0

    for follow in follows:
        if follow.user == poster:
            following = following + 1
        if follow.user_followed == poster:
            followers = followers + 1

    # Display posts
    allposts = Post.objects.all().order_by("-time")
    postlist = []
    for post in allposts:
        if post.poster == poster:
            postlist.append(post)

    # Pagination
    p = Paginator(postlist, 10)
    page = request.GET.get('page')
    posts = p.get_page(page)

    likeslist = []
    if user is not None:
        likes = Like.objects.filter(user = user)
        for like in likes:
            likeslist.append(like.post.id)

    return render(request, "network/profile.html", {
        "user":user,
        "posts":posts,
        "poster":poster,
        "followers":followers,
        "following":following,
        "editpost":EditPost(),
        "likeslist": likeslist
    })

@login_required
def following(request):

    user = User.objects.get(username = request.user.username)
    allposts = Post.objects.all().order_by("-time")
    follows = Following.objects.all()
    postlist = []

    for post in allposts:
        for follow in follows:
            if follow.user == user and post.poster == follow.user_followed:
                postlist.append(post)

    # Pagination
    p = Paginator(postlist, 10)
    page = request.GET.get('page')
    posts = p.get_page(page)

    likeslist = []
    likes = Like.objects.filter(user = user)
    for like in likes:
        likeslist.append(like.post.id)

    return render(request, "network/following.html", {
        "posts": posts,
        "editpost":EditPost(),
        "likeslist": likeslist
    })


# API routes
@csrf_exempt
@login_required
def follow(request): 
    follows = Following.objects.all()

    # Check if is follower, returns boolean
    if request.method == "POST":
        body = json.loads(request.body)
        thisuser = body.get('user')
        thisposter = body.get('poster')
        isfollower = False
        for follow in follows:
            if follow.user.username == thisuser and follow.user_followed.username == thisposter:
                isfollower = True
        return JsonResponse({"isfollower": isfollower}, status=201)

    # Follow or unfollow the poster
    if request.method == "PUT":
        body = json.loads(request.body)
        thisuser = User.objects.get(username = body.get('user'))
        thisposter = User.objects.get(username = body.get('poster'))
        isfollower = False
        for follow in follows:
            if follow.user == thisuser and follow.user_followed == thisposter:
                isfollower = True
        if isfollower:
            unfollow = Following.objects.filter(user = thisuser).filter(user_followed = thisposter)
            unfollow.delete()
            return HttpResponseRedirect(f"/profile/{thisposter}")
        else:
            newfollower = Following(user = thisuser, user_followed = thisposter)
            newfollower.save()
            return HttpResponseRedirect(f"/profile/{thisposter}")

@csrf_exempt
@login_required   
def edit(request):


    if request.method == "POST":
        # Get the values
        body = json.loads(request.body)
        id = body.get('id')
        text = body.get('text')
        

        # Update post in the database
        thispost = Post.objects.get(id = id)
        thispost.text = text
        thispost.save()
        return JsonResponse({"status": "post updated"}, status=201)
    
@csrf_exempt
@login_required
def like(request): 
  
    if request.method == "POST":
        # Get the values
        body = json.loads(request.body)
        user = User.objects.get(username = body.get('user'))
        post = Post.objects.get(id = body.get('id'))
        newlike = Like(user=user, post=post)
        newlike.save()

        post.likecount= F('likecount') + 1
        post.save()
        print(post.likecount)

        return JsonResponse({"counter": f"plusone"}, status=201)

@csrf_exempt
@login_required
def unlike(request): 
  
    if request.method == "POST":
        # Get the values
        body = json.loads(request.body)
        user = User.objects.get(username = body.get('user'))
        post = Post.objects.get(id = body.get('id'))

        unlike = Like.objects.filter(user = user).filter(post = post)
        unlike.delete()

        post.likecount= F('likecount') - 1
        post.save()

        return JsonResponse({"counter": "minusone"}, status=201)


# User management routes
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))
    
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
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "network/register.html")