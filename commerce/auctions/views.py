from email.mime import image
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Listing, User, Bid, Comment


class NewListing(forms.Form):
    title = forms.CharField(max_length=64, label="Title", widget=forms.TextInput(attrs={"placeholder": "Title"}))
    description = forms.CharField(max_length=1000, label="Description", widget=forms.Textarea(attrs={"placeholder": "Description"}))
    starting_bid = forms.DecimalField(label="StartingBid", max_digits=20, decimal_places=2, widget=forms.TextInput(attrs={"placeholder": "Starting Price"}))
    image = forms.URLField(required=False, max_length=1000, label="Image", widget=forms.TextInput(attrs={"placeholder": "Image URL"}))
    category = forms.ChoiceField(required=False, choices=[('', 'Category'), ('ELE', 'Electronics'), ('FAS', 'Fashion'), ('ART', 'Art'), ('HOM', 'Home'), ('BOO', 'Books'), ('SPO', 'Sports')], label="Category")

class NewComment(forms.Form):
    pass

class NewBid(forms.Form):
    pass


def index(request):
    listings = Listing.objects.all() # For listing in listings
    return render(request, "auctions/index.html", {"listings": listings})
        

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
        return render(request, "auctions/login.html", {
            "message": "Invalid username and/or password."
        })
    return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/register.html")


def create(request): # There can be vaious posts with the same name because the listing id is different
    if request.method == "POST":
        form = NewListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = float(form.cleaned_data["starting_bid"])
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            #get current user object
            user = User.objects.get(pk=request.user.id)
            # create listing
            newlisting = Listing(owner=user, publisher=user, title=title, description=description, starting_bid=starting_bid, image=image, category=category)
            # add newlisting to the database
            newlisting.save()
            # redirects to that listing page
            return HttpResponseRedirect(f"/listing/{newlisting.id}")

    return render(request, "auctions/create.html", {
        "newlistingform": NewListing(),
})


def listing(request, id):
    
    item = Listing.objects.get(id=id)
    watchers = item.watched_by.all()
    publisher = item.publisher
    winner = ""
    highestbid = ""
    minbid = item.starting_bid
    comments = []
    bids = Bid.objects.order_by("-price")

    for bid in bids:
        if bid.listing_id.id == int(id): # Find the highest bidder and the min bid
            winner = User.objects.get(pk=bid.user_id.id)
            highestbid = bid.price
            minbid = highestbid + 1
            item.starting_bid = highestbid # update to current price to display everywhere
            item.save()
            break

    if Comment.objects.filter(listing_id=id).exists():# If any, gather only this listing's comments
        allcomments = Comment.objects.all()
        for allcomment in allcomments:
            if allcomment.listing_id == item:
                comments.append(allcomment)

    if User.objects.filter(pk=request.user.id).exists(): # Start loged-in version
        user = User.objects.get(pk=request.user.id)

        if request.method == "POST":

            # 1 Watchlist add / remove button
            if user in item.watched_by.all() and request.POST.get("removewatchlist"):
                item.watched_by.remove(user)
            if user not in item.watched_by.all() and request.POST.get("addwatchlist"):
                item.watched_by.add(user)

            # 2 Bid
            if request.POST.get("newbid") and minbid <= float(request.POST.get("newbid")):
                newbid = Bid(user_id=user, listing_id=item, price=request.POST.get("newbid"))
                newbid.save()
                return HttpResponseRedirect(f"/listing/{item.id}")

            # 3 Close auction
            if request.POST.get("close"):
                item.is_active=False # Auction is now closed
                item.owner=winner # Publisher transfers ownership of the listed item
                item.save()
                return HttpResponseRedirect(f"/listing/{item.id}")

            # 4 Comment
            if request.POST.get("newcomment"):
                newcomment = Comment(user_id=user, listing_id=item, comment=request.POST.get("newcomment"))
                newcomment.save()
                return HttpResponseRedirect(f"/listing/{item.id}")
    
        return render(request, "auctions/listing.html", { # End Loged-in version
            "user": user,
            "listing": item,
            "watchers": watchers,
            "minbid": minbid,
            "publisher": publisher,
            "highestbid": highestbid,
            "winner": winner,
            "comments": comments
            })

    return render(request, "auctions/listing.html", { # Not signed version
        "listing": item,
        "watchers": watchers,
        "minbid": minbid,
        "publisher": publisher,
        "highestbid": highestbid,
        "winner": winner,
        "comments": comments
        })


def watchlist(request):
    if User.objects.filter(pk=request.user.id).exists(): # only loged-in
        user = User.objects.get(pk=request.user.id)
        listings = Listing.objects.all()
        watchlist = []

        for listing in listings: # If user in watclisted_by, append listing
            listingwatchers = listing.watched_by.all()
            for watcher in listingwatchers:
                if user == watcher:
                    watchlist.append(listing) 

        return render(request, "auctions/watchlist.html", {"watchlist": watchlist})
    return render(request, "auctions/watchlist.html")


def categories(request): # intoduce the category selector
    return render(request, "auctions/categories.html")


def category(request, category):

    code = "" # First I need to get the code of the category I'm watching
    listings = Listing.objects.all()
    catlist = []

    ELECTRONICS = "ELE"
    FASHION = "FAS"
    ART = "ART"
    HOME = "HOM"
    BOOKS = "BOO"
    SPORTS = "SPO"

    CATEGORIES = [
        (ELECTRONICS, "Electronics"),
        (FASHION, "Fashion"),
        (ART, "Art"),
        (HOME, "Home"),
        (BOOKS, "Books"),
        (SPORTS, "Sports")
    ]

    for cat in CATEGORIES: # Current category code
        if cat[1] == category.capitalize():
            code=cat[0]
    for listing in listings: # Every active listing with same code 
        if listing.category == code and listing.is_active == True and len(listing.category) == 3:
            catlist.append(listing)
    return render(request, "auctions/category.html", {"catlist":catlist, "category":category})
