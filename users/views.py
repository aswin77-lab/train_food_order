from django.shortcuts import get_object_or_404, render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

from superadmin.models import Station, TrainRoute
from vendors.models import FoodItem, Vendor
from .models import CustomUser, Order, Trip
from django.contrib.auth.hashers import check_password

def get_user_from_session(request):
    user_id = request.session.get("user_id")
    if user_id:
        return get_object_or_404(CustomUser, id=user_id)
    return None


def user_register(request):
    if request.method == "POST":
        # Get form data from the POST request
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Basic validation: check if the passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "user_register.html")
        
        # Check if the email is already registered
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "user_register.html")
        
        # Create the user.
        # We use the email as the username for simplicity.
        user = CustomUser.objects.create_user(username=email, email=email, password=password)
        user.name = name
        user.phone = phone
        user.gender = gender
        
        try:
            user.age = int(age)
        except (ValueError, TypeError):
            user.age = None
        
        user.save()

        messages.success(request, "Registration successful. Please log in.")
        return redirect("user_login")  # Replace with the URL name of your user login view
    else:
        return render(request, "user_register.html")
    




def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "user_login.html")
        
        if check_password(password, user.password):
            # Store the user's ID in the session for manual session-based auth.
            request.session["user_id"] = user.id
            messages.success(request, "Logged in successfully.")
            return redirect("user_dashboard")  # Adjust URL name as needed
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "user_login.html")
    else:
        return render(request, "user_login.html")


def user_logout(request):
    if "user_id" in request.session:
        del request.session["user_id"]
    messages.success(request, "Logged out successfully.")
    return redirect("user_login")  # Adjust URL name as needed


def user_dashboard(request):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to access the dashboard.")
        return redirect("user_login")
    orders = Order.objects.filter(user=user).order_by('-order_time')
   
    context = {
        "user": user,
        'orders': orders
    }
    return render(request, "user_dashboard.html", context)




from django.db.models import Q

def trip_search_results(request):
    # Retrieve all stations for the search form
    stations = Station.objects.all()
    
    # Get search parameters
    start_station_id = request.GET.get("start_station")
    end_station_id = request.GET.get("end_station")
    travel_date = request.GET.get("travel_date")
    
    train_routes = []
    if start_station_id and end_station_id and travel_date:
        train_routes = TrainRoute.objects.filter(
            Q(source_station_id=start_station_id) | Q(intermediate_stops__id=start_station_id),
            Q(destination_station_id=end_station_id) | Q(intermediate_stops__id=end_station_id)
        ).distinct()
        
    context = {
        "stations": stations,
        "train_routes": train_routes,
        "travel_date": travel_date,
    }
    return render(request, "search_and_results.html", context)





def trip_book(request, route_id):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to access the dashboard.")
        return redirect("user_login")
    if request.method == "POST":
        travel_date = request.POST.get("travel_date")
        train_route = get_object_or_404(TrainRoute, id=route_id)
        
        # Create the trip booking for the logged-in user
        trip = Trip.objects.create(
            user=user,  # Use the user retrieved from session
            train_route=train_route,
            travel_date=travel_date,
        )
        messages.success(request, f"Trip booked successfully! Your PNR is {trip.pnr}.")
        return redirect("user_dashboard")
    else:
        messages.error(request, "Invalid request.")
        return redirect("trip_search")


def trip_detail(request):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to access the dashboard.")
        return redirect("user_login")
    trips = Trip.objects.filter(user=user).order_by('-booking_time')
    context = {
        'trips': trips,
    }
    return render(request, "trip_detail.html", context)







def search_food_by_pnr(request):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to search for food.")
        return redirect("user_login")
    
    pnr = request.GET.get('pnr', '').strip().upper()
    vendors = []
    trip = None
    if pnr:
        try:
            # Restrict search to trips belonging to the logged-in user
            trip = Trip.objects.get(pnr=pnr, user=user)
            
            # Get the train route from the trip
            route = trip.train_route
            
            # Build a list of station IDs from source, destination, and intermediate stops
            station_ids = [route.source_station.id, route.destination_station.id]
            intermediate_ids = list(route.intermediate_stops.values_list('id', flat=True))
            station_ids.extend(intermediate_ids)
            
            # Filter vendors whose near_station is in the list of station_ids
            vendors = Vendor.objects.filter(near_station__id__in=station_ids)
            
        except Trip.DoesNotExist:
            messages.error(request, "No trip found for the provided PNR.")
    
    context = {
        'pnr': pnr,
        'trip': trip,
        'vendors': vendors,
    }
    return render(request, "search_food.html", context)



def vendor_food_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    food_items = FoodItem.objects.filter(vendor=vendor)
    context = {
        'vendor': vendor,
        'food_items': food_items,
    }
    return render(request, "vendor_food_detail.html", context)




def order_food(request, food_id):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to order food.")
        return redirect("user_login")
    
    food_item = get_object_or_404(FoodItem, id=food_id)
    
    if request.method == "POST":
        quantity = request.POST.get("quantity")
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect("order_food", food_id=food_id)
        
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect("order_food", food_id=food_id)
        
        if quantity > food_item.quantity:
            messages.error(request, f"Insufficient quantity available. Only {food_item.quantity} available.")
            return redirect("order_food", food_id=food_id)
        
        total_price = food_item.price * quantity
        
        # Create the order with vendor info
        order = Order.objects.create(
            user=user,
            food_item=food_item,
            vendor=food_item.vendor,  # Add vendor information
            quantity=quantity,
            total_price=total_price
        )
        
        # Reduce the quantity in FoodItem and save
        food_item.quantity -= quantity
        food_item.save()
        
        messages.success(request, f"Order placed successfully! Order ID: {order.id}")
        return redirect("user_dashboard")
    
    return render(request, "order_food.html", {"food_item": food_item})


def user_order_list(request):
    user = get_user_from_session(request)
    if not user:
        messages.error(request, "Please log in to view your orders.")
        return redirect("user_login")
    
    orders = Order.objects.filter(user=user).order_by('-order_time')
    context = {
        'orders': orders,
    }
    return render(request, "user_order_list.html", context)
