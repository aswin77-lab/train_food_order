from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from superadmin.models import Station
from users.models import Order
from .models import FoodItem, Vendor
from django.contrib.auth import logout


# Helper function to retrieve the Vendor from session
def get_vendor_from_session(request):
    vendor_id = request.session.get("vendor_id")
    if vendor_id:
        return get_object_or_404(Vendor, id=vendor_id)
    return None

def vendor_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        near_station_id = request.POST.get("near_station")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            stations = Station.objects.all()
            return render(request, "vendor_register.html", {"stations": stations})
        
        if Vendor.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            stations = Station.objects.all()
            return render(request, "vendor_register.html", {"stations": stations})
        
        hashed_password = make_password(password)
        
        Vendor.objects.create(
            name=name,
            phone=phone,
            email=email,
            password=hashed_password,
            near_station_id=near_station_id if near_station_id else None,
        )
        messages.success(request, "Vendor registered successfully. Please log in.")
        return redirect("vendor_login")
    
    else:
        stations = Station.objects.all()
        return render(request, "vendor_register.html", {"stations": stations})

def vendor_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            vendor = Vendor.objects.get(email=email)
        except Vendor.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "vendor_login.html")
        
        if not vendor.is_approved:
            messages.error(request, "Your account is not approved by the admin.")
            return render(request, "vendor_login.html")

        if check_password(password, vendor.password):
            request.session["vendor_id"] = vendor.id  # Set vendor id in session
            messages.success(request, "Logged in successfully.")
            return redirect("vendor_dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "vendor_login.html")
    else:
        return render(request, "vendor_login.html")



def vendor_dashboard(request):
    vendor = get_vendor_from_session(request)
    if not vendor:
        messages.error(request, "Please log in as vendor.")
        return redirect("vendor_login")
    
    # Fetch pending orders
    pending_orders = Order.objects.filter(vendor=vendor, status="Pending")
    notifications = [
        {"message": f"New order #{order.id} is pending", "link": f"/vendors/vendor_order_list/{order.id}"}
        for order in pending_orders
    ]
    notifications_count = len(notifications)

    # Fetch all orders
    orders = Order.objects.filter(vendor=vendor)

    context = {
        "vendor": vendor,
        "notifications": notifications,
        "notifications_count": notifications_count,
        "orders": orders,
    }
    return render(request, "vendor_dashboard.html", context)



def vendor_food_list(request):
    vendor = get_vendor_from_session(request)
    if not vendor:
        messages.error(request, "Please log in as vendor.")
        return redirect("vendor_login")
    
    pending_orders = Order.objects.filter(vendor=vendor, status="Pending")
    notifications = [
        {"message": f"New order #{order.id} is pending", "link": f"/vendors/vendor_order_list/{order.id}"}
        for order in pending_orders
    ]
    notifications_count = len(notifications)
    
    food_items = FoodItem.objects.filter(vendor=vendor)
    context = {
        'vendor': vendor,
        'food_items': food_items,
        "notifications_count": notifications_count,
    }
    return render(request, "vendor_food_list.html", context)


def vendor_add_food(request):
    vendor = get_vendor_from_session(request)
    if not vendor:
        messages.error(request, "Please log in as vendor.")
        return redirect("vendor_login")
    pending_orders = Order.objects.filter(vendor=vendor, status="Pending")
    notifications = [
        {"message": f"New order #{order.id} is pending", "link": f"/vendors/vendor_order_list/{order.id}"}
        for order in pending_orders
    ]
    notifications_count = len(notifications)
    
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        image = request.FILES.get("image")

        
        if not all([name, price, quantity, image]):
            messages.error(request, "All fields are required.")
            return redirect("vendor_add_food")
        
        FoodItem.objects.create(
            vendor=vendor,
            name=name,
            price=price,
            quantity=quantity,
            image=image
        )
        messages.success(request, "Food item added successfully!")
        return redirect("vendor_food_list")
    else:
        context = {
            'vendor': vendor,
            "notifications_count": notifications_count,
        }
        return render(request, "vendor_add_food.html", context)



def vendor_order_list(request):
    vendor = get_vendor_from_session(request)  # Fetch vendor from session

    if not vendor:
        return redirect('vendor_login')  # Redirect if vendor is not authenticated
    pending_orders = Order.objects.filter(vendor=vendor, status="Pending")
    notifications = [
        {"message": f"New order #{order.id} is pending", "link": f"/vendors/vendor_order_list/{order.id}"}
        for order in pending_orders
    ]
    notifications_count = len(notifications)
    orders = Order.objects.filter(vendor=vendor) # Fetch vendor's orders

    context = {
        'vendor': vendor,
        'orders': orders,
         "notifications_count": notifications_count,
      
    }
    return render(request, 'vendor_order_list.html', context)

def update_order_status(request, order_id):
    vendor =get_vendor_from_session(request)
    order = get_object_or_404(Order, id=order_id, vendor=vendor)
    
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    
    return redirect('vendor_order_list')



def vendor_logout(request):
    logout(request)
    request.session.flush()  # Clear any vendor-related session data
    return redirect("vendor_login") 




def vendor_edit_food(request, food_id):
    vendor = get_vendor_from_session(request)
    if not vendor:
        messages.error(request, "Please log in as vendor.")
        return redirect("vendor_login")
    
    food_item = get_object_or_404(FoodItem, id=food_id, vendor=vendor)
    
    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()
        if not new_name:
            messages.error(request, "Food name cannot be empty.")
            return redirect("vendor_edit_food", food_id=food_item.id)
        
        # Update food item fields
        food_item.name = new_name
        food_item.price = request.POST.get("price")
        food_item.quantity = request.POST.get("quantity")
        if "image" in request.FILES:
            food_item.image = request.FILES.get("image")
        food_item.save()
        
        messages.success(request, "Food item updated successfully!")
        return redirect("vendor_food_list")
    
    pending_orders = Order.objects.filter(vendor=vendor, status="Pending")
    notifications = [
        {"message": f"New order #{order.id} is pending", "link": f"/vendors/vendor_order_list/{order.id}"}
        for order in pending_orders
    ]
    notifications_count = len(notifications)
    orders = Order.objects.filter(vendor=vendor) # Fetch vendor's orders
    
    context = {
        'vendor': vendor,
        'food_item': food_item,
        'notifications': notifications,
        'notifications_count': notifications_count,
    }
    return render(request, "vendor_edit_food.html", context)


def vendor_delete_food(request, food_id):
    vendor = get_vendor_from_session(request)
    if not vendor:
        messages.error(request, "Please log in as vendor.")
        return redirect("vendor_login")
    if request.method == "POST":
        FoodItem.objects.filter(id=food_id).delete()
        
        messages.success(request, "Food item deleted successfully!")
    
    # Redirect to the food list after deletion.
    return redirect("vendor_food_list")