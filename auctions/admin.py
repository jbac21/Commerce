from django.contrib import admin

from .models import User, Listing, Comment, Bid, Watchlist

# Register your models here.
class ListingAdmin (admin.ModelAdmin):
    list_display = ("id", "title", "description", "startingBid", 'highestBid', "status", "url", "category", "seller", "buyer")
    list_filter = ["category", "highestBid", "seller", "buyer"]
    search_fields = ("id", "title")

class BidAdmin (admin.ModelAdmin):
    list_display = ("id", "bid", "user", "listing")

class UserAdmin (admin.ModelAdmin):
    list_display = ("id", "username")

class CommentAdmin (admin.ModelAdmin):
    list_display = ("id", "user", "listing", "text", "date")

class WatchlistAdmin (admin.ModelAdmin):
    list_display = ("id", "user", "listing", "status")

admin.site.register(Listing, ListingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Comment, CommentAdmin)