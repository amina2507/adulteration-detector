from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import os
import torch
import shutil
import logging
import pandas
from PIL import Image
import os
import logging
import torch
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import pytz
from datetime import datetime



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'media/uploads/'


logging.basicConfig(filename=os.path.join(BASE_DIR, 'app.log'), level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

try:
    model_directory = os.path.join(BASE_DIR, "cnn", "yolov5")  # Updated model_directory path
    model = torch.hub.load(model_directory, 'custom', path='best.pt', source='local')
    logger.error("Successful loading of model!")
    logger.error(f"model: {model}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")

def home(request):
    return render(request, 'home.html')

def detect_fruit(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        if uploaded_file and allowed_file(uploaded_file.name, ALLOWED_EXTENSIONS):  
            fs = FileSystemStorage()
            filename = fs.save(os.path.join(BASE_DIR, UPLOAD_FOLDER, uploaded_file.name), uploaded_file)
           
            return redirect('uploaded_file', filename=filename)
    return render(request, 'detect_fruit.html')

def uploaded_file(request, filename):
    try:
        image_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, filename)
        results = model(image_path, size=416)
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return HttpResponse("An error occurred while processing the image.")

    if len(results.pandas().xyxy) > 0:
        results.print()
        save_dir = os.path.join(BASE_DIR, UPLOAD_FOLDER, filename)
        # Saving the original image
        original_image_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, "original_" + filename)
        shutil.copyfile(image_path, original_image_path)
        # Removing the processed image
        os.remove(image_path)
        results.save(save_dir=save_dir)

        def and_syntax(alist):
            if len(alist) == 1:
                return alist[0]
            elif len(alist) == 2:
                return " and ".join(alist)
            elif len(alist) > 2:
                return ", ".join(alist[:-1]) + ", and " + alist[-1]
            else:
                return ""

        confidences = results.pandas().xyxy[0]['confidence'].tolist()
        format_confidences = [f"{round(percent*100)}%" for percent in confidences]
        format_confidences_str = and_syntax(format_confidences)
        
        labels = results.pandas().xyxy[0]['name'].tolist()
        labels = set(labels)
        labels = [emotion.capitalize() for emotion in labels]
        labels_str = and_syntax(labels)
        confidence_threshold = 0.98
        is_ripe_with_adulteration = any(confidence >= confidence_threshold for confidence in confidences)
        if is_ripe_with_adulteration:
            ripeness_status = f" Adulterated (Not Safe to eat)"
        else:
            ripeness_status = f"Unadulterated (Safe to eat)"
        filenames=filename
        username = None
        if request.user.is_authenticated:
            username = request.user.username
            india_timezone = pytz.timezone('Asia/Kolkata')
            current_time = datetime.datetime.now(india_timezone)
            # Save the image details to the database
            image = images.objects.create(
                user_name=username,
                image=filename,
                date_created=current_time,
                result=ripeness_status
            )
        return render(request, 'results.html', {'confidences': format_confidences_str,
                                                 'labels': labels_str,
                                                 'old_filename': filename,
                                                 'filename': filename,
                                                 'ripeness_status': ripeness_status,
                                                 'uploaded_image': True})
    else:
        return render(request, 'results.html', {'labels': '1',
                                                 'old_filename': filename,
                                                 'filename': filename,
                                                 'ripeness_status': "No fruit detected",
                                                 'uploaded_image': False})

def download_file(request, filename):
    file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    return HttpResponse("The requested file does not exist.")


from django.shortcuts import render, redirect
from . models import *
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, auth
from . decorators import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from datetime import date
from django.core import serializers
import json
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.utils import timezone
import json
from django.shortcuts import render

@login_required
@logged_inn2

def admin_home(request):        # for displaying admin home page
    bok = Registration.objects.get(id=request.session['logg'])
    gtt = Registration.objects.filter(User_role='admin')
    df = Registration.objects.get(User_role='admin')
    context = {
        'bok': bok,
        'df': df,
        'gtt': gtt,

    }
    return render(request, 'admin_home.html', context)

def logged_out(request):     # for logout the current session
    del request.session['logg']
    auth.logout(request)
    if 'logg' in request.session:
        del request.session['logg']
        return redirect('home')
    return redirect('home')

from django.core.exceptions import MultipleObjectsReturned

def login(request):     #  for login admin/user
    if request.method == 'POST':
        username = request.POST.get("user_name")
        password = request.POST.get("pword")
        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Username or Password is Incorrect')
            return render(request, 'login.html')
        auth.login(request, user)
        try:
            registration = Registration.objects.get(user=user, Password=password)
            usertype = registration.User_role
            if usertype == 'admin':
                request.session['logg'] = registration.id
                return redirect("admin_home")
            elif usertype == 'employee':
                request.session['logg'] = registration.id
                registration.save()
                return redirect('employee_home')
            else:
                messages.error(request, 'Your access to the website is blocked. Please contact admin')
                return render(request, 'login.html')
        except Registration.DoesNotExist:
            messages.error(request, 'Username or password entered is incorrect')
            return render(request, 'login.html')
        except MultipleObjectsReturned:
            registrations = Registration.objects.filter(user=user, Password=password)
            return render(request, 'choose_account.html', {'registrations': registrations})
    else:
        return render(request, 'login.html')


def delete_admin(request, id):
    bb1 = Registration.objects.get(id = id)
    User.objects.get(email = bb1.Email).delete()
    messages.success(request, 'You have successfully resigned from administration')
    return redirect('home')

def edit_admin(request):        # for edit admin
    gtt = Registration.objects.filter(User_role = 'admin')
    bb1 = Registration.objects.get(User_role = 'admin')
    um = User.objects.get(email=bb1.Email)
    return render(request, 'update_adminn.html',{'bb1':bb1,'um':um,'gtt':gtt})

def admin_rg(request):      #for register admin
    if request.method == 'POST':
        lk = Registration.objects.all()
        for t in lk:
            if t.User_role == 'admin':
                messages.success(request, 'You are not allowed to be registered as admin')
                return redirect('login')
        x = datetime.datetime.now()
        z = x.strftime("%Y-%m-%d")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pnm = request.POST.get('pnm')
        psw = request.POST.get('psw')
        admin = request.POST.get('adminn1')
        reg1 = Registration.objects.all()
        for i in reg1:
            if i.Email == email:
                messages.success(request, 'User already exists')
                return render(request, 'register_admin.html')
        user_name = request.POST.get('user_name')
        for t in User.objects.all():
            if t.username == user_name:
                messages.success(request, 'Username taken. Please try another')
                return render(request, 'register_admin.html')
        user = User.objects.create_user(username=user_name, email=email, password=psw)
        user.save()
        t = Registration()
        t.First_name = first_name
        t.Last_name = last_name
        t.Email = email
        t.Mobile_Number = pnm
        t.Password = psw
        t.Registration_date = z
        t.User_role = admin
        t.user = user
        t.save()
        messages.success(request, 'You have successfully registered as admin')
        return redirect('login')
    else:
        return render(request, 'register_admin.html')

def bnb(request):       #for edit admin
    bb1 = Registration.objects.get(User_role='admin')
    um = User.objects.get(email=bb1.Email)
    if request.method == 'POST':
        first = request.POST.get('first')
        last = request.POST.get('last')
        em = request.POST.get('em')
        psw = request.POST.get('psw')
        user_name = request.POST.get('user_name')
        m = User.objects.all().exclude(username = um.username)
        for t in m:
            if t.username == user_name:
                messages.success(request, 'Username taken. Please try another')
                return render(request, 'update_admin.html',{'bb1':bb1,'um':um})
        passwor = make_password(psw)
        df = Registration.objects.get(id=request.session['logg'])
        kmk = df.user.pk
        kmk = User.objects.get(id=kmk)
        kmk.username = user_name
        kmk.password = passwor
        kmk.email = em
        kmk.save()
        user = auth.authenticate(username = user_name, password = psw)
        auth.login(request,user)
        dcd = Registration.objects.get(User_role = 'admin')
        dcd.Email = em
        dcd.Password = psw
        dcd.First_name = first
        dcd.Last_name = last
        dcd.user = kmk
        dcd.save()
        b = Registration.objects.get(User_role='admin')
        m = int(b.id)
        request.session['logg'] = m
        gtt = Registration.objects.filter(User_role='admin')
        messages.success(request, 'You have successfully updated your profile')
        return render(request, 'login.html', {'gtt': gtt})
    else:
        return render(request, 'update_admin.html')


def edit_adminn(request):
    bb1 = Registration.objects.get(User_role = 'admin')
    um = User.objects.get(email=bb1.Email)
    return render(request, 'update_adminn.html',{'bb1':bb1,'um':um})
        
def del_admin(request, id):
    bb1 = Registration.objects.get(id = id)
    User.objects.get(email = bb1.Email).delete()
    messages.success(request, 'You have successfully resigned from administration')
    return redirect('home')





def logout(request):
    del request.session['logg']
    auth.logout(request)
    if 'logg' in request.session:
        del request.session['logg']
        return redirect('home')
    return redirect('home')

    
def adminn_details(request):        # for displaying admin profile
    bok = Registration.objects.get(id=request.session['logg'])
    gtt = Registration.objects.filter(User_role = 'admin')
    return render(request, "adminn_details.html",{'bok':bok,'gtt':gtt,})


@login_required
@logged_inn4
def employee_home(request):     #for display user homepage
    bok = Registration.objects.get(id=request.session['logg'])
    gtt = Registration.objects.filter(User_role='employee')
    df = Registration.objects.filter(User_role='employee').first() 
    k = Registration.objects.all()

    context = {
        'k': k,
        'df': df,
        'gtt': gtt,
        'bok':bok,
    }
    return render(request, 'employee_home.html', context)


from django.shortcuts import render
from .models import Registration
def employeess(request):        # for displaying all users
    bok = Registration.objects.get(id=request.session['logg'])
    all_users = Registration.objects.filter(User_role='employee')
    return render(request, "employees.html", {'all_users': all_users,'bok':bok})

def delete_admin(request, id):
    bb1 = Registration.objects.get(id = id)
    User.objects.get(email = bb1.Email).delete()
    messages.success(request, 'You have successfully resigned from administration')
    return redirect('login')

def register_employee(request):     #for register user
    if request.method == 'POST':
        x = datetime.datetime.now()
        z = x.strftime("%Y-%m-%d")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        psw = request.POST.get('psw')
        employee = request.POST.get('employee')
        reg1 = Registration.objects.all()
        for i in reg1:
            if i.Email == email:
                messages.success(request, 'User already exists')
                return render(request, 'login.html')
        user_name = request.POST.get('user_name')
        for t in User.objects.all():
            if t.username == user_name:
                messages.success(request, 'Username taken. Please try another')
                return render(request, 'login.html')
        user = User.objects.create_user(username=user_name, email=email, password=psw)
        user.save()
        t = Registration()
        t.First_name = first_name
        t.Last_name = last_name
        t.Email = email
        t.Password = psw
        t.Mobile_Number = mobile_number
        t.Registration_date = z
        t.User_role = employee
        t.user = user
        t.save()
        messages.success(request, 'You have Successfully Registered')
        return redirect('login')
    else:
        return render(request, 'login.html')

def update_employee(request):       # for edit user
        b = Registration.objects.get(id=request.session['logg'])
        bok = Registration.objects.get(id=request.session['logg'])
        um = User.objects.get(email=b.Email)
        if request.method == 'POST':
            f_name = request.POST.get('first_name')
            l_name = request.POST.get('last_name')
            email = request.POST.get('email')
            psw = request.POST.get('psw')
            user_name = request.POST.get('user_name')
            m = User.objects.all().exclude(username=um.username)
            for t in m:
                if t.username == user_name:
                    messages.success(request, 'Username taken. Please try another')
                    return render(request, 'update_employee.html', {'bb': b, 'um': um,})
            passwords = make_password(psw)
            u = User.objects.get(email=b.Email)
            u.password = passwords
            u.username = user_name
            u.email = email
            u.save()
            user = auth.authenticate(username=user_name, password=psw)
            auth.login(request, user)
            try:
                b.First_name = f_name
                b.Last_name = l_name
                b.Email = email
                b.Password = psw
                b.user = u
                b.save()
                messages.success(request, 'Your Profile Updated')
                return render(request, 'login.html')
            except:
                b.First_name = f_name
                b.Last_name = l_name
                b.Email = email
                b.Password = psw
                b.user = u
                b.save()
                messages.success(request, 'Profile updated')
                return render(request, 'login.html')
        return render(request, 'update_employee.html',{'bok':bok})

def del_employee(request, id):      
    bb1 = Registration.objects.get(id = id)
    User.objects.get(email = bb1.Email).delete()
    messages.success(request, 'Account Deleted')
    return redirect('admin_home')

def logged_out(request):
    del request.session['logg']
    auth.logout(request)
    if 'logg' in request.session:
        del request.session['logg']
        return redirect('home')
    return redirect('home')


from django.core.exceptions import MultipleObjectsReturned

def login(request):
    if request.method == 'POST':
        username = request.POST.get("user_name")
        password = request.POST.get("pword")
        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Username or Password is Incorrect')
            return render(request, 'login.html')
        auth.login(request, user)
        
        try:
            registration = Registration.objects.get(user=user, Password=password)
            usertype = registration.User_role
            if usertype == 'admin':
                request.session['logg'] = registration.id
                return redirect("admin_home")
            elif usertype == 'employee':
                request.session['logg'] = registration.id
                registration.save()
                return redirect('employee_home')
            else:
                messages.error(request, 'Your access to the website is blocked. Please contact admin')
                return render(request, 'login.html')
        except Registration.DoesNotExist:
            messages.error(request, 'Username or password entered is incorrect')
            return render(request, 'login.html')
        except MultipleObjectsReturned:
          
            registrations = Registration.objects.filter(user=user, Password=password)
            return render(request, 'choose_account.html', {'registrations': registrations})
    else:
        return render(request, 'login.html')
    


def del_new_user(request, id):
    bb1 = Registration.objects.get(id = id)
    User.objects.get(email = bb1.Email).delete()
    messages.success(request, 'Account Deleted')
    return redirect('admin_home')

def view(request):

    if 'logg' in request.session:
        registrations = Registration.objects.all()
        bok = Registration.objects.get(id=request.session['logg'])
        all_users = Registration.objects.filter(User_role='employee')
        return render(request, "view.html", {'registrations': registrations, 'all_users': all_users,'bok':bok})
    else:
        return redirect('login')


from django.shortcuts import render
from .models import Feedback

def v_feedback(request):

    feedbacks = Feedback.objects.select_related('registration__user').all()
    
    return render(request, "feedbacks.html", {'feedbacks': feedbacks})     


def upload_images(request):
    upload_items=images.objects.all()
    return render(request,"uploaded_images.html",{"upload_items":upload_items})

def delete_uploads(request, upload_id):  # for deleting feedback

    uploads = get_object_or_404(images, pk=upload_id)

    uploads.delete()

    return redirect('upload_images')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feedback, Registration

@login_required
def feedback(request):      #for add feedback
    if request.method == 'POST':

        comments = request.POST.get('comments', None) 
        rating = request.POST.get('rating', None)  

        registration = request.user.registration 

        feedback = Feedback.objects.create(
            registration=registration,
            comments=comments,
            rating=rating
        )

        return redirect('employee_home')
    else:

        registrations = Registration.objects.all()
        return render(request, "feedback.html", {'registrations': registrations})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Feedback

def delete_feedback(request, feedback_id):  # for deleting feedback

    feedback = get_object_or_404(Feedback, pk=feedback_id)

    feedback.delete()

    return redirect('v_feedback')


from django.shortcuts import render
from .models import Feedback
def list_feedback(request):         #for displaying feedback
    feedbacks = Feedback.objects.select_related('registration__user').all()
    return render(request, "feedback.html", {'feedbacks': feedbacks})




from django.shortcuts import render, redirect
from . models import *
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

def mailing(request):
    if request.method=="POST":
        name=request.POST['name']
        user_email=request.POST['email']
        phone=request.POST['phone']
        msg=request.POST['msg']
        details = f"User email: {user_email}\nName: {name}\nPhone: {phone}\nMessage: {msg}"
        send_mail(
        name,
        details,
        'myproject258@gmail.com',
        ['myproject258@gmail.com'],
        fail_silently=False,
        )
        messages.success(request, 'Email successfully Send!')
        return render(request,'home.html')
    return render(request,'home.html')



from django.core.mail import send_mail

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Registration.objects.get(Email=email)

            send_mail(
                'Forgot Password Request',
                f'Your username is: {user.user}\nYour password is: {user.Password}',
                'myproject258@gmail.com', 
                [email],
                fail_silently=False,
            )
            message = "Username and password have been sent to your email."
        except Registration.DoesNotExist:
            message = "Email does not exist."

        return render(request, "forgot_password.html", {'message': message})

    else:

        return render(request, "forgot_password.html")
