from unicodedata import bidirectional, name
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser): # New User: Name1 = User(name="Diego", email=a@a.a, password="1234")
    pass


class Listing(models.Model): # New Listing: Item1 = Listing(publisher=????, tittle="PC", description="tldr", starting_bid=30, image="", category="ART")

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

    is_active = models.BooleanField(default=True) # Active by default
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publications") # user who publishes the listing
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="possessions") # if is_active = False, transfer ownership to highest bidder
    title = models.CharField(max_length=64)# initial input
    description = models.CharField(max_length=1000) # initial imput
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2) # initial input
    image = models.URLField(max_length=1000, blank=True, null=True) # Internet URL
    category = models.CharField(max_length=3, choices=CATEGORIES, blank=True) # Chose among the 6 categories
    time = models.DateTimeField(auto_now_add=True) # Automatic time of creation
    watched_by = models.ManyToManyField(User, blank=True, related_name="watchers") # If user is among watchers, listing appears in watchlist
    
    def __str__(self):
        return f"{self.id}: {self.title}"


class Bid(models.Model): # New Bid: bid1 = Bid(user= listing= price=35 )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="biddedlistings")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: User {self.user_id} bidded in listing {self.listing_id} ({self.price}$)"


class Comment(models.Model): # New Comment: Comment1 = Comment(user= listing= comment="hehe")
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, related_name="commenters") # Comments are protected even if the user deletes the account
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commentedlistings")
    comment = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.id}: User {self.user_id} commented in {self.listing_id} ({self.comment}$)"