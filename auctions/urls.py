from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("view_listing/<int:listing_id>", views.view_listing, name="view_listing"),
    path("terminate_listing/<int:listing_id>", views.terminate_listing, name="terminate_listing"),
    path("comment/<int:listing_id>", views.comment, name="comment"),    
    path("categories", views.categories, name="categories"),    
    path("watchlist", views.watchlist, name="watchlist"),       
    path("watchlist_action/<int:listing_id>", views.watchlist_action, name="watchlist_action"),    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
