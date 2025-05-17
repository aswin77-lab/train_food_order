from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import CustomUser, Order
from vendors.models import Vendor
from .models import Station, TrainRoute

# Login view – after successful authentication, store admin_id in session.
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                request.session['admin_id'] = user.id  # Save admin id in session
                return redirect("admin_dashboard")  # Update URL name as needed
            else:
                messages.error(request, "You are not authorized to access the admin area.")
                return render(request, "admin_login.html")
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, "admin_login.html")
    else:
        return render(request, "admin_login.html")

# Helper function to check if the user is an admin.
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    admin_id = request.session.get("admin_id")
    admin_user = get_object_or_404(CustomUser, id=admin_id)

    # Fetching actual counts from the database
    total_users = CustomUser.objects.exclude(is_superuser=True).count()  # Excluding admin
    total_orders = Order.objects.count()  # Fetch total orders
    total_vendors = Vendor.objects.count()  # Fetch total vendors
    vendors_approval = Vendor.objects.filter(is_approved=True).count()  # Vendors approved

    context = {
        'admin': admin_user,
        'total_users': total_users-1,
        'total_orders': total_orders,
        'total_vendors': total_vendors,
        'vendors_approval': vendors_approval,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == "POST":
        # Prevent an admin from deleting themselves.
        if request.session.get("admin_id") == user_id:
            messages.error(request, "You cannot delete yourself!")
        else:
            CustomUser.objects.filter(id=user_id).delete()
            messages.success(request, "User deleted successfully.")
        return redirect("user_list")
    else:
        users = CustomUser.objects.all()
        return render(request, "user_list.html", {"users": users})

def admin_logout(request):
    logout(request)
    request.session.flush()  # Clear session data.
    return redirect("admin_login")

def add_train_route(request):
    if request.method == "POST":
        train_number = request.POST.get("train_number")
        train_name = request.POST.get("train_name")
        source_station_id = request.POST.get("source_station")
        destination_station_id = request.POST.get("destination_station")
        intermediate_stops_ids = request.POST.getlist("intermediate_stops")
        departure_time = request.POST.get("departure_time")
        arrival_time = request.POST.get("arrival_time")
        days_of_operation = request.POST.get("days_of_operation")
        
        route = TrainRoute.objects.create(
            train_number=train_number,
            train_name=train_name,
            source_station_id=source_station_id,
            destination_station_id=destination_station_id,
            departure_time=departure_time,
            arrival_time=arrival_time,
            days_of_operation=days_of_operation
        )
        if intermediate_stops_ids:
            route.intermediate_stops.set(intermediate_stops_ids)
        messages.success(request, "Train route added successfully!")
        return redirect("add_train_route")
    
    stations = Station.objects.all()
    return render(request, "add_train_route.html", {"stations": stations})

def add_station(request):
    if request.method == "POST":
        station_name = request.POST.get("station_name")
        if station_name:
            station, created = Station.objects.get_or_create(name=station_name)
            if created:
                messages.success(request, f"Station '{station_name}' added successfully!")
            else:
                messages.info(request, f"Station '{station_name}' already exists.")
            return redirect("add_station")
    return render(request, "add_station.html")

def train_list(request):
    train_routes = TrainRoute.objects.all()
    return render(request, "train_list.html", {"train_routes": train_routes})


def user_list(request):
    users = CustomUser.objects.all()
    return render(request, "user_list.html", {"users": users})



@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, "vendors_list.html", {"vendors": vendors})

@login_required
def approve_vendor(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    vendor.is_approved = True
    vendor.save()
    return redirect("vendor_list")

@login_required
def disapprove_vendor(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    vendor.is_approved = False
    vendor.save()
    return redirect("vendor_list")


@login_required
def orders_list(request):
    orders = Order.objects.all().order_by('-id')
    return render(request, 'admin_orders_list.html', {'orders': orders})