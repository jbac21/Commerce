from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from datetime import datetime

from .models import User, Listing, Bid, Comment, Watchlist


# List of categories for listings
categoriesItems = [
    "Select category",
    "Brooms",
    "Caldrons",
    "Wands",
    "Cloaks",
    "Hats",
    "Animals",
    "Others"
]

# Prepare categories for Django form
categoriesTotal = list(range(1,len(categoriesItems)+1))
categoriesTotal.insert(0,"")

strCategoriesTotal = []
for item in categoriesTotal:
    strCategoriesTotal.append(str(item))
categoryFormList = list(zip(strCategoriesTotal, categoriesItems))

# Django forms in use
class listingForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder' : 'Title'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder' : 'Description'}))
    startingBid = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'placeholder' : 'Starting Bid'}))
    url = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder' : 'Image-url'}))
    category = forms.ChoiceField(choices=categoryFormList, required=False)

class bidForm(forms.Form):
    price = forms.DecimalField()

class commentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder' : 'Comment'}))

class searchForm(forms.Form):
    category = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput(), initial={'category': "{{category}}"})


def index(request):

    # Access index page
    if request.method == "GET":
        # Get all current listings
        listing = Listing.objects.filter(status="active")

        # Render active listings
        return render(request, "auctions/index.html", {
            "auctions": listing
        })

    # Filter active listings
    else:
        # Get category data
        categoryTerm = request.POST.get('category')

        # Get index for category according to list of tuples (categoryFormList)
        for element in categoriesItems:
            if element == categoryTerm:
                categoryTerm = categoriesItems.index(element)

        # Get listings for category
        listing = Listing.objects.filter(status='active', category=categoryTerm)

        # Render active listings
        return render(request, "auctions/index.html", {
            "auctions": listing
        })


@login_required
def create_listing(request):
    # Render page for creating listings
    if request.method == "GET":
        return render(request, "auctions/newListing.html", {
            'form' : listingForm
        })

    # Create new listing
    else:
        form = listingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            
            f = Listing(
                title=title,
                description=form.cleaned_data["description"],
                startingBid=form.cleaned_data["startingBid"],
                url=form.cleaned_data["url"],
                category=form.cleaned_data["category"],
                seller= User.objects.get(pk=request.user.id)
                )
            f.save()

            return HttpResponseRedirect("/")


def view_listing(request, listing_id):
    
    # Retrieve information about listing
    listing = Listing.objects.get(id=listing_id)
    form = bidForm()
    commentText = Comment.objects.filter(listing=listing.id)
    global categoryFormList
    try:
        user = User.objects.get(pk=request.user.id)
    except:
        user = None 
    try: 
        watchstatus = Watchlist.objects.get(user=user, listing=listing, status='active')
    except:
        watchstatus = None
    if listing.category != "":
        category = categoriesItems[int(listing.category)]
    else:
        category = None

    # Bid
    if request.method == "POST" and request.user.is_authenticated:

        # Check for currently highest Bid
        if listing.highestBid == None:
            highestBid = listing.startingBid
        else:
            highestBid = listing.highestBid

        # Get form input value
        form = bidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["price"]   

            # If requirements for bidding not fulfilled:
            if bid < highestBid:
                error = True
                return render(request, "auctions/listing.html", {
                    'listing' : listing,
                    'form': form,
                    'error': error,
                    'comments': commentText,
                    'commentForm' : commentForm(),
                    'watchlist' : watchstatus
                })   

            # Requirements for bidding are fulfilled:
            else:
                
                if listing.status == 'active':
                    # Create bid instance
                    f = Bid(
                        bid=bid,
                        user=user,
                        listing=listing
                        )
                    f.save()

                    # Update listing table
                    listing.highestBid = bid 
                    listing.buyer = user
                    listing.save()
                  
                return render(request, "auctions/listing.html", {
                    'listing' : listing,
                    'form': bidForm(),
                    'comments': commentText,
                    'commentForm' : commentForm(),
                    'watchlist' : watchstatus,
                    'category' : category
                })                           
    
    
    # Show auction
    else:

        return render(request, "auctions/listing.html", {
            'listing' : listing,
            'form': form,
            'comments': commentText,
            'commentForm' : commentForm(),
            'watchlist' : watchstatus,
            'category' : category
        }) 

@login_required
def terminate_listing(request, listing_id):

    # Terminate auction
    if request.method == "POST":
        
        # Get listing
        listing = Listing.objects.get(id=listing_id)  
        commentText = Comment.objects.filter(listing=listing.id)

        # Prepare forms for httpresponse
        form = bidForm()

        # Update information    
        listing.status = 'deactivate'
        listing.save()

        address = "/view_listing/" + str(listing.id)
        return HttpResponseRedirect(address)
    
    # Route to index page
    else:
        return HttpResponseRedirect('/')        


@login_required
def comment(request, listing_id):

    if request.method == "POST":
        
        # Get data
        date_time = datetime.now().timestamp()
        commentText = commentForm(request.POST)
        if commentText.is_valid():
            comment= commentText.cleaned_data["comment"]      

        # Create Comment
        f = Comment(
            user = User.objects.get(pk=request.user.id),
            listing = Listing.objects.get(id=listing_id),
            text = comment,
            date = date_time
        )
        f.save()

        address = "/view_listing/" + str(listing_id)
        return HttpResponseRedirect(address)

    # Route to index page
    else:
        return HttpResponseRedirect('/')              


@login_required
def watchlist_action(request, listing_id):
    
    # Get data
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(id=listing_id)
    try:
        results = Watchlist.objects.get(user=user, listing=listing) # Search for watchlist element
    except:
        results = None


    # Add to watchlist
    if request.method == 'GET':

        # Element has already been added to watchlist, status is changed
        if results != None:
            print("None")
            # Activate watchlist item
            results.status = 'active'
            results.save()
            print(results.status)
            address = "/view_listing/" + str(listing_id)
            return HttpResponseRedirect(address)

        # Add new element to watchlist
        else:
            print("else")
            # Create new Watchlist Instance
            f = Watchlist(
                user = user,
                listing = listing,
                status='active'
            )
            f.save()
            print(f.status)
            # Redirect to auction
            address = "/view_listing/" + str(listing_id)
            return HttpResponseRedirect(address)

    # Remove from watchlist
    else:
        results.status = 'inactive'
        results.save()

        address = "/view_listing/" + str(listing_id)
        return HttpResponseRedirect(address)


@login_required
def watchlist(request):

    listingsID = []
    for entry in Watchlist.objects.filter(user=User.objects.get(pk=request.user.id), status="active").values():
        listingsID.append(entry['listing_id'])

    listings = Listing.objects.filter(id__in=listingsID).values()

    return render(request, "auctions/watchlist.html", {
        'watchlists': listings
    })      


@login_required
def categories(request):
    
    # Show a list of all categories
    if request.method == "GET":

        return render(request, "auctions/categories.html", {
            'categories' : categoriesItems[1:],
            'form' : searchForm()
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
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
    else:
        return render(request, "auctions/register.html")
