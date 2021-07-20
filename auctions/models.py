from django.contrib.auth.models import AbstractUser # Comes along with pw, username, etc.
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    startingBid = models.DecimalField(decimal_places=2, max_digits=20)
    highestBid = models.DecimalField(decimal_places=2, max_digits=20, blank=True, null=True)
    url = models.CharField(max_length=1000)
    category  = models.CharField(max_length=100)
    seller = models.ForeignKey(User, related_name='seller_set', on_delete=models.PROTECT)
    buyer = models.ForeignKey(User, related_name='buyer_set', on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=100, default='active') 

class Bid(models.Model):
    bid = models.DecimalField(decimal_places=2, max_digits=20)
    user = models.ForeignKey(User, related_name='user_set', on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, related_name='listing_set', on_delete=models.PROTECT)

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='cuser_set', on_delete=models.PROTECT, null=True)
    listing = models.ForeignKey(Listing, related_name='clisting_set', on_delete=models.PROTECT, null=True)
    text = models.CharField(max_length=3000, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name='wuser_set', on_delete=models.PROTECT, null=True)
    listing = models.ForeignKey(Listing, related_name='wlisting_set', on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=100, null=True, default="active")