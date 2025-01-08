from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid, Comment, Category, Watchlist
from .forms import ListingForm, BidForm, CommentForm

def index(request):
    print(f"Soy request --- >>> {request.user}")
    print(f"Soy request --- >>> {request}")
    listings = Listing.objects.filter(active=True)
    users = User.objects.all()
    print(f"SOY user ---QuerySet--- >>> {users}")
    print(" ----- 1 -------------- ")
    users_json = User.objects.all().values()
    print(f"SOY user_json ----- >>> {users_json}")
    # categories = Category.objects.all()   ESTO NO HACE NADA AQUI
    return render(request, "auctions/index.html", {
        "listings": listings,
        # "categories": categories        
    })

def datos_globales(request):
    count = 0
    if request.user.is_authenticated:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        count = watchlist_items.count()
    return {
        'count_watch_list': count
    }

#   login_view _ logout_view _ register fucntions
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
  
# - - - --  -

@login_required
def create_listing(request):
    categories = Category.objects.all()

    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            return redirect("index")
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {
        "form": form,
        "categories": categories
        })

# Listing Page view
def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bids = listing.bids.all().order_by("-amount")  # Assuming reverse chronological order
    comments = listing.comments.all().order_by("-timestamp")
    user_watchlist = Watchlist.objects.filter(user=request.user, listing=listing) if request.user.is_authenticated else None

    if request.method == "POST":
        # Handle Bid
        if "place_bid" in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.listing = listing
                bid.user = request.user
                if bid.amount >= listing.starting_bid and (not bids or bid.amount > bids[0].amount):
                    bid.save()
                    listing.current_price = bid.amount
                    listing.save()
                    messages.success(request, "Bid placed successfully!")
                else:
                    messages.error(request, "Bid must be higher than current bid and starting bid.")
        # Handle Comment
        elif "add_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.listing = listing
                comment.user = request.user
                comment.save()
                messages.success(request, "Comment added successfully!")

    bid_form = BidForm()
    comment_form = CommentForm()
    current_bids = listing.bids.all().order_by("-amount")
    print(f'Aqui ------>>>>> {current_bids}')
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": current_bids,
        "comments": comments,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "in_watchlist": user_watchlist.exists() if user_watchlist else False,
    })

# Watchlist view
@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist_items})


# Categories view
def categories(request):
    categories = Category.objects.all()
    
#     categories = Listing.objects.values('category').distinct()
 
#    return render(request, "auctions/index.html", {"categories": categories})
    return render(request, "auctions/categories.html", {"categories": categories})


# Category Listings view
def category_listings(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category_listings.html", {"category": category, "listings": listings})


def add_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user

    # Check if the listing is already in the user's watchlist
    in_watchlist = Watchlist.objects.filter(user=user, listing=listing).exists()

    if request.method == "POST":
        if in_watchlist:
            # If it's already in the watchlist, remove it
            Watchlist.objects.filter(user=user, listing=listing).delete()
        else:
            # If it's not in the watchlist, add it
            Watchlist.objects.create(user=user, listing=listing)
        return redirect('listing_page', listing_id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "in_watchlist": in_watchlist
    })


def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user

    # Check if the listing is already in the user's watchlist
    in_watchlist = Watchlist.objects.filter(user=user, listing=listing).exists()

    if request.method == "POST":
        if in_watchlist:
            # If it's already in the watchlist, remove it
            Watchlist.objects.filter(user=user, listing=listing).delete()
       
        return redirect('listing_page', listing_id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "in_watchlist": in_watchlist
    })


def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        listing.active = False
        listing.save()
        return redirect('index')


def close_listings(request):
    listings = Listing.objects.filter(active=False)
    # categories = Category.objects.all()       ESTO NO HACE NADA AQUI
    return render(request, "auctions/close_listings.html", {
        "listings": listings,
        # "categories": categories        
    })