from django.shortcuts import render, redirect
from .models import Worker, Attendance, UserProfile
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, time

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

        # ❌ Block if no active slot
        if active_slot is None:
            return render(request, "home.html", {
                "workers": workers,
                "active_slot": None,
                "error": "Attendance can only be filled during active slot time!"
            })

        slot = active_slot.id   # ✅ THIS IS THE IMPORTANT PART

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

    # GET request
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
        name = request.POST.get("name")
        dob = request.POST.get("dob")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        photo = request.FILES.get("photo")

        Worker.objects.create(
            name=name,
            dob=dob,
            phone=phone,
            email=email,
            photo=photo
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
        login_type = request.POST.get("login_type")  # user or admin

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # If admin selected
            if login_type == "admin":
                if user.is_staff or user.is_superuser:
                    return redirect("/admin/")
                else:
                    logout(request)
                    return render(request, "login.html", {"error": "You are not an admin."})

            # If user selected
            if user.is_staff:
                return redirect("home")
            else:
                return redirect("user_dashboard")

        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        dob = request.POST.get("dob")
        email = request.POST.get("email")
        photo = request.FILES.get("photo")

        # Username check
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        # Email check
        if UserProfile.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "This email is already registered"
            })

        # Create Django User
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name,
            email=email or ""
        )

        # Create Profile
        profile = UserProfile.objects.create(
            user=user,
            mobile=mobile,
            dob=dob,
            photo=photo,
            email=email
        )

        # ----- CREATE WORKER AUTOMATICALLY -----
        from .models import Worker

        if not Worker.objects.filter(email=email).exists():
            Worker.objects.create(
                name=name,
                dob=dob,
                phone=mobile,
                email=email,
                photo=photo
            )

        return redirect("login")

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

        # Photo (both can change)
        photo = request.FILES.get("photo")
        if photo:
            profile.photo = photo

        # Fields everyone can change
        profile.dob = request.POST.get("dob")
        profile.email = request.POST.get("email")

        # Only admin can change name & mobile
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

    # Find worker using email (reliable key)
    worker = Worker.objects.filter(email=request.user.email).first()

    if not worker:
        return render(request, "user_dashboard.html", {
            "records": [],
            "error": "Your worker profile is not linked. Contact admin."
        })

    records = Attendance.objects.filter(
        worker=worker
    ).order_by("-date")

    return render(request, "user_dashboard.html", {
        "records": records
    })


# ================= DOWNLOAD ATTENDANCE PDF =================
@login_required
def download_attendance(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed here.")

    today = date.today()

    records = Attendance.objects.filter(date=today, present=True).select_related("worker")

    slot1 = records.filter(slot=1)
    slot2 = records.filter(slot=2)
    slot3 = records.filter(slot=3)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{today}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Worker Attendance Report")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Date: {today}")
    y -= 30

    def draw_slot(title, queryset):
        nonlocal y
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, y, title)
        y -= 20

        p.setFont("Helvetica", 11)

        if queryset.exists():
            for i, rec in enumerate(queryset, 1):
                p.drawString(70, y, f"{i}. {rec.worker.name}")
                y -= 18
        else:
            p.drawString(70, y, "No one present.")
            y -= 18

        y -= 15

    draw_slot("Slot 1 (9:00 - 10:00)", slot1)
    draw_slot("Slot 2 (1:00 - 2:00)", slot2)
    draw_slot("Slot 3 (4:00 - 5:00)", slot3)

    p.showPage()
    p.save()

    return response
@login_required
def edit_worker(request, worker_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed here.")

    worker = Worker.objects.get(id=worker_id)

    if request.method == "POST":
        worker.name = request.POST.get("name")
        worker.dob = request.POST.get("dob")
        worker.phone = request.POST.get("phone")
        worker.email = request.POST.get("email")

        photo = request.FILES.get("photo")
        if photo:
            worker.photo = photo

        worker.save()
        return redirect("add_worker")

    return render(request, "edit_worker.html", {"worker": worker})
from .models import Slot

def get_current_slot():
    now = datetime.now().time()

    slots = Slot.objects.filter(is_active=True)

    for slot in slots:
        if slot.start_time <= now <= slot.end_time:
            return slot

    return None
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

            # Only update if both times are provided
            if start_val and end_val:
                slot.start_time = start_val
                slot.end_time = end_val

            slot.is_active = True if active_val else False

            slot.save()

        return redirect("manage_slots")

    return render(request, "manage_slots.html", {"slots": slots})
