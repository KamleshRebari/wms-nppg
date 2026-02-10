from django.shortcuts import render, redirect
from .models import Worker, Attendance, UserProfile, Slot
from datetime import date, datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden

# For PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ================= HOME (ADMIN ONLY) =================
@login_required
def home(request):
    if not request.user.is_staff:
        return redirect("user_dashboard")

    workers = Worker.objects.all()
    active_slot = get_current_slot()

    if request.method == "POST":

        if active_slot is None:
            return render(request, "home.html", {
                "workers": workers,
                "active_slot": None,
                "error": "Attendance can only be filled during active slot time!"
            })

        slot = active_slot.id

        for worker in workers:
            checkbox_name = f"present_{worker.id}"
            present = checkbox_name in request.POST

            Attendance.objects.update_or_create(
                worker=worker,
                date=date.today(),
                slot=slot,
                defaults={"present": present}
            )

        return redirect("home")

    return render(request, "home.html", {
        "workers": workers,
        "active_slot": active_slot
    })


# ================= ADD WORKER (ADMIN ONLY) =================
@login_required
def add_worker(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed here.")

    if request.method == "POST":
        Worker.objects.create(
            name=request.POST.get("name"),
            dob=request.POST.get("dob"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            photo=request.FILES.get("photo")
        )
        return redirect("add_worker")

    workers = Worker.objects.all()
    return render(request, "add_worker.html", {"workers": workers})


# ================= DISPLAY / RECORDS (ADMIN ONLY) =================
@login_required
def display(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed here.")

    today = date.today()

    records = Attendance.objects.filter(date=today, present=True).select_related("worker")

    slot1 = records.filter(slot=1)
    slot2 = records.filter(slot=2)
    slot3 = records.filter(slot=3)

    context = {
        "today": today,
        "slot1": slot1,
        "slot2": slot2,
        "slot3": slot3,
    }

    return render(request, "blog/display.html", context)


# ================= LOGIN =================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        login_type = request.POST.get("login_type")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if login_type == "admin":
                if user.is_staff or user.is_superuser:
                    return redirect("/admin/")
                else:
                    logout(request)
                    return render(request, "login.html", {"error": "You are not an admin."})

            if user.is_staff:
                return redirect("home")
            else:
                return redirect("user_dashboard")

        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":

        debug = []

        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            name = request.POST.get("name")
            mobile = request.POST.get("mobile")
            dob = request.POST.get("dob")
            email = request.POST.get("email")
            photo = request.FILES.get("photo")

            if User.objects.filter(username=username).exists():
                return render(request, "register.html", {"error": "Username already exists"})

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=name,
                email=email or ""
            )

            UserProfile.objects.create(
                user=user,
                mobile=mobile,
                dob=dob or "2000-01-01",
                photo=photo,
                email=email
            )

            Worker.objects.create(
                name=name,
                dob=dob or "2000-01-01",
                phone=mobile,
                email=email,
                photo=photo
            )

            return redirect("login")

        except Exception as e:
            return render(request, "register.html", {
                "error": f"ERROR: {str(e)}"
            })

    return render(request, "register.html")


# ================= PROFILE =================
@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "mobile": "",
            "dob": "2000-01-01",
        }
    )

    if request.method == "POST":

        photo = request.FILES.get("photo")
        if photo:
            profile.photo = photo

        profile.dob = request.POST.get("dob")
        profile.email = request.POST.get("email")

        if request.user.is_staff:
            request.user.first_name = request.POST.get("name")
            profile.mobile = request.POST.get("mobile")
            request.user.save()

        profile.save()
        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})


# ================= USER DASHBOARD =================
@login_required
def user_dashboard(request):

    worker = Worker.objects.filter(email=request.user.email).first()

    if not worker:
        return render(request, "user_dashboard.html", {
            "records": [],
            "error": "Your worker profile is not linked. Contact admin."
        })

    records = Attendance.objects.filter(worker=worker).order_by("-date")

    return render(request, "user_dashboard.html", {
        "records": records
    })


# ================= SLOT HELPER =================
def get_current_slot():
    now = datetime.now().time()

    slots = Slot.objects.filter(is_active=True)

    for slot in slots:
        if slot.start_time <= now <= slot.end_time:
            return slot

    return None


# ================= MANAGE SLOTS =================
@login_required
def manage_slots(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    slots = Slot.objects.all()

    if request.method == "POST":
        for slot in slots:

            start_val = request.POST.get(f"start_{slot.id}")
            end_val = request.POST.get(f"end_{slot.id}")
            active_val = request.POST.get(f"active_{slot.id}")

            if start_val and end_val:
                slot.start_time = start_val
                slot.end_time = end_val

            slot.is_active = True if active_val else False
            slot.save()

        return redirect("manage_slots")

    return render(request, "manage_slots.html", {"slots": slots})
@login_required

def edit_worker(request, worker_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    worker = Worker.objects.get(id=worker_id)

    if request.method == "POST":
        worker.name = request.POST.get("name")
        worker.phone = request.POST.get("phone")
        worker.dob = request.POST.get("dob")
        worker.email = request.POST.get("email")

        if request.FILES.get("photo"):
            worker.photo = request.FILES.get("photo")

        worker.save()
        return redirect("add_worker")

    return render(request, "edit_worker.html", {"worker": worker})
