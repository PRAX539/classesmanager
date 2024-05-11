from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .tokens import account_activation_token  
from django.contrib.auth.models import User  
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from datetime import datetime,timedelta
from django.core.mail import EmailMessage,send_mail
from django.contrib import messages
from django.db.models import Q,Sum
from .models import *
from .forms import *
from io import BytesIO
from django.template.loader import get_template
import calendar
import logging



def landing_page(request):


    return render(request,'landing_page.html')
# Create your views here.
def loginpage(request):
    login_errors = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if len(username) == 0 or len(password) == 0:
            login_errors = 'Invalid Credentials'

        user = authenticate(username = username, password = password)
        if user is not None:
            login(request,user)
            messages.success(request,"Logged Successfully")
            return redirect ('dashboard')
        else:
            login_errors = 'Invalid Credentials'
            
    
    return render(request,'loginpage.html',{'login_errors':login_errors})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            current_site = get_current_site(request)
            mail_subject = "Reset Password"
            message = render_to_string("password_reset_email.html", {
                'user': get_user_model().objects.get(email=email),
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(get_user_model().objects.get(email=email).pk)),
                'token': account_activation_token.make_token(get_user_model().objects.get(email=email)),
            })
            to_email = email
            email = EmailMessage(mail_subject,message,"test@dnpsfinance.in",[to_email])
            email.send(fail_silently = False)

            return render(request,"reset_password_done.html")
        except Exception  as e :
           return render(request,'forgot_password.html',{'message':e})

        
    return render(request, 'forgot_password.html')



def password_reset_confirm(request,uidb64,token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        return redirect("change_password",user = user.pk)



    return render(request, "password_reset_confirm.html")

def change_password(request,user):

    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password :
            user = CustomUser.objects.get(pk = user)
            user.set_password(password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('loginpage')
        else:
            return render(request,'change_password.html',{'message':'Password does not match'})
    return render(request,'change_password.html')

def logoutpage(request):
    messages.error(request,"Logged Out Succesfully")
    logout(request)

    return redirect('loginpage')

def registeruser(request):
    if request.method =="POST":
        form = registrationform(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = False
            user.save()  
            # to get the domain of the current site  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('acc_active_email.html', {  
                    'user': user,  
                    'domain': current_site.domain,  
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                    'token':account_activation_token.make_token(user),  
                })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                            mail_subject, message, to=[to_email]  
                )  
            email.send(fail_silently=False)
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = registrationform()
    return render(request,'registeruser.html',{'form':form})



def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return render (request, 'email_confirmation.html')  
    else:  
        return HttpResponse('Activation link is invalid!') 

@login_required
def dashboard(request):
    if first_day_of_month(request):
        calculated_monthly_fees(request)
    after_schedules = daily_schedule.objects.filter(user = request.user).filter(schedule_date__gte = datetime.today()).order_by('schedule_date')
    calculated_daily_fees(request)
    monthly_income = income_details.objects.filter(user = request.user).filter(income_date__year = datetime.today().year).filter(income_date__month = datetime.today().month).aggregate(Sum('income_amount'))['income_amount__sum'] or 0
    yearly_income = income_details.objects.filter(user = request.user).filter(income_date__year = datetime.today().year).aggregate(Sum('income_amount'))['income_amount__sum'] or 0
    lectures_taken = daily_schedule.objects.filter(user = request.user).filter(schedule_date__year = datetime.today().year).count() or 0
   
    context = {
        'after_schedules':after_schedules,
        'monthly_income': monthly_income,
        'yearly_income': yearly_income,
        'lectures_taken':lectures_taken
    }

    return render(request,"dashboard.html",context)

#  This need to change and check with last login whether the month have changed or not  this is not working properly
@login_required
def first_day_of_month(request):
    date_obj = datetime.now()
    if date_obj == 1:
        return True
    else:
        return False


@login_required
def calculated_monthly_fees(request):
    distinct_subject = set()
    pending_schedules = daily_schedule.objects.filter(user = request.user).filter(schedule_date__lt = datetime.today()).filter(calculated = False)  
    for pending in pending_schedules:
        if pending.subject.method_of_payment == "fixed per month":
            pending.calculated = True
            pending.save()
            if pending not in distinct_subject:
                distinct_subject.add(pending)
                   
    for pending in distinct_subject:  
        amount = pending.subject.number_field
        fixed_data = income_details.objects.create(user = request.user, subject = pending.subject, income_date = datetime.today(),income_amount = amount, income_description = " Monthly payment")
        fixed_data.save()

    return
    


@login_required
def calculated_daily_fees(request):
    pending_schedules = daily_schedule.objects.filter(user = request.user).filter(schedule_date__lt = datetime.today()).filter(calculated = False)    
    for pending in pending_schedules:
        if pending.subject.method_of_payment == "hourwise":
            rates = pending.subject.number_field
            start_datetime = datetime.combine(pending.schedule_date, pending.start_time)
            end_datetime = datetime.combine(pending.schedule_date, pending.end_time)
            hours_worked = (end_datetime - start_datetime).total_seconds() / 3600
            amount = hours_worked * float(rates)
            
            hour_data = income_details.objects.create(user = request.user, subject = pending.subject, income_date = pending.schedule_date,income_amount = amount, income_description = "hourly payment")
            hour_data.save()
            pending.calculated = True
            pending.save()
            
            
        elif pending.subject.method_of_payment == "lecturewise":
            amount = pending.subject.number_field
            lecture_data = income_details.objects.create(user = request.user, subject = pending.subject, income_date = pending.schedule_date,income_amount = amount, income_description = "Lecturewise payment")
            lecture_data.save()
            pending.calculated = True
            pending.save()

    return 



#  This need work and login building

@login_required
def recalculate(request):
    if request.method =="POST":
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()




    return render(request,"recalculate.html")


@login_required
def professor_profile(request):
    user = request.user
    userid = request.user.id
    user_details = additional_data.objects.get(user = userid)
    form = additional_data_form(instance = user_details)
    form2 = edit_profile_form(instance = user)
    
    if request.method == "POST":
        form = additional_data_form(request.POST,request.FILES,instance = user_details)
        form2 = edit_profile_form(request.POST,instance = user)
        
        if form.is_valid() and form2.is_valid():
            form.save(commit=False)
            form2.save(commit = False)
            form.user = request.user
            form2.user  = request.user
            form.save()
            form2.save()
            messages.success(request,"Your Profile has beed updated!!")
            return redirect("dashboard")
        
        

    return render(request,"professor_profile.html",{'form':form,'form2':form2,})



@login_required
def classes_list(request):
    class_list  = classes.objects.filter(user = request.user).filter(disabled = False)
    return render(request,"classes_list.html",{'class_list':class_list})

def add_classes(request):
    class_list  = classes.objects.filter(user = request.user).filter(disabled = False)
    if request.method =="POST":
        form = classesform(request.POST)
        if form.is_valid():
            form.save(commit = False)
            form.instance.user = request.user
            form.save()
            messages.success(request,"Institute added successfully")
            return redirect("add_classes")

    else:
        form = classesform()    
    
    return render(request,'add_classes.html',{'class_list':class_list,'form':form})


@login_required
def edit_classes(request,id):
    class_id = classes.objects.get(id = id)
    class_list = classes.objects.filter(user = request.user).filter(disabled = False)
    form = classesform(request.POST or None, instance = class_id)
    if form.is_valid():
        form.save()
        messages.success(request,"Institute updated successfully")
        return redirect("add_classes")

    return render (request,"edit_classes.html",{'form':form,'class_list':class_list,'id':id})


@login_required
def delete_classes(request,id):
    class_id = classes.objects.get(id = id)
    class_list = classes.objects.filter(user = request.user).filter(disabled = False)
    if request.method == "POST":
        class_id.disabled = True
        class_id.save()
        messages.success(request,"Institute deleted successfully")
        return redirect("add_classes")

    

    return render (request,"delete_classes.html",{'class_list':class_list,'class_id':class_id})


@login_required
def standard_list(request):
    std_list = standard.objects.all().filter(user = request.user).filter(disabled = False)
    

    return render(request,"standard_list.html",{'std_list':std_list})


@login_required
def add_standard(request):
    std_list = standard.objects.all().filter(user = request.user).filter(disabled = False)
    if request.method =="POST":
        form = standardform(request.POST)
        if form.is_valid():
            form.save(commit = False)
            form.instance.user = request.user
            form.save()
            messages.success(request,"Standard added successfully")
            return redirect("add_standard")
        

    else:
        form = standardform()    

    return render(request,"add_standard.html",{'form':form, 'std_list':std_list})


@login_required
def edit_standard(request,id):
    std_id = standard.objects.get(id = id)
    std_list = standard.objects.all().filter(user = request.user).filter(disabled = False)
    form = standardform(request.POST or None, instance = std_id)
    if form.is_valid():
        form.save()
        messages.success(request,"Standard updated successfully")
        return redirect("add_standard")

    return render (request,"edit_standard.html",{'form':form,'std_list':std_list,'id':id})

  
@login_required
def delete_standard(request,id):
    std_id = standard.objects.get(id = id)
    std_list = standard.objects.all().filter(user = request.user).filter(disabled = False)
    if request.method == "POST":
        std_id.disabled = True
        std_id.save()
        messages.success(request,"Standard deleted successfully")
        return redirect("add_standard")


    return render(request,"delete_standard.html",{'std_list':std_list,'std_id':std_id})


@login_required
def subject_list(request):
    sub_list = subject.objects.filter(user = request.user).filter(disabled=False)

    return render(request,"subject_list.html",{'sub_list':sub_list})

@login_required
def add_subject(request):
    sub_list = subject.objects.filter(user = request.user).filter(disabled=False)
    if request.method =="POST":
        form = subjectform(request.POST)
        if form.is_valid():
            subjectconf = form.save(commit = False)
            subjectconf.user = request.user
            subjectconf.save()
            messages.success(request,"Subject added successfully")
            return redirect("add_subject")
        
    else:
        form = subjectform(user = request.user)

    return render(request,"add_subject.html",{'form':form,'sub_list':sub_list})

@login_required
def edit_subject(request,id):
    sub_list = subject.objects.filter(user = request.user).filter(disabled=False)
    sub_id = subject.objects.get(id = id)
    form = subjectform(request.POST or None, instance = sub_id, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request,"Subject updated successfully")
        return redirect("add_subject")
    

    return render (request,"edit_subject.html",{'form':form,'sub_list':sub_list,'id':id})


@login_required
def delete_subject(request,id):
    sub_id = subject.objects.get(id = id)
    sub_list = subject.objects.filter(user = request.user).filter(disabled=False)
    if request.method == "POST":
        sub_id.disabled = True
        sub_id.save()
        messages.success(request,"Subject deleted successfully")
        return redirect("add_subject")


    return render(request,"delete_subject.html",{'sub_list':sub_list,'sub_id':sub_id})


@login_required
def schedule_list(request):
    schedule_list = daily_schedule.objects.filter(user = request.user)

    return render(request,"schedule_list.html",{'schedule_list':schedule_list})


@login_required
def add_schedule(request):
    schedule_list = daily_schedule.objects.filter(user = request.user).order_by('-schedule_date')
    if request.method =="POST":
        form = daily_schedule_form(request.POST)
        if form.is_valid():
            form.save(commit = False)
            form.instance.user = request.user
            form.save()
            messages.success(request,"Schedule added successfully")
            return redirect("add_schedule")
        
    else:
        form = daily_schedule_form(user = request.user)

    return render(request,"add_schedule.html",{'form':form,'schedule_list':schedule_list})


@login_required
def edit_schedule(request,id):
    schedule_list = daily_schedule.objects.filter(user = request.user)
    schedule_id = daily_schedule.objects.get(id = id)
    form = daily_schedule_form(request.POST or None, instance = schedule_id, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request,"Schedule updated successfully")
        return redirect("add_schedule")
  

    

    return render (request,"edit_schedule.html",{'form':form,'schedule_list':schedule_list,'id':id})


@login_required
def delete_schedule(request,id):
    schedule_list = daily_schedule.objects.filter(user = request.user)
    schedule_id = daily_schedule.objects.get(id = id)
    if request.method == "POST":
        schedule_id.delete()
        messages.success(request,"Schedule deleted successfully")
        return redirect("add_schedule")


    return render(request,"delete_schedule.html",{'schedule_list':schedule_list,'schedule_id':schedule_id})


@login_required
def reports(request):

    return render(request,"reports.html",{})


@login_required
def classeswise_income(request):
    class_list  = classes.objects.filter(user = request.user)
    if request.method == "POST":
        final_data = []
    
        selected_class = request.POST.get('selected_class')
        filter_subject = subject.objects.filter(user = request.user).filter(classes = selected_class)
        for i in filter_subject:
            
            income_data = income_details.objects.filter(subject = i)
            for j in income_data:
                final_data.append(j)
        
        return render(request,"classeswise_income.html",{'final_data':final_data,})


    

    return render(request,"classeswise_income.html",{'class_list':class_list})

@login_required
def whats_next(request):

    return render(request,"whats_new.html")


@login_required
def standardwise_income(request):
    standard_list = standard.objects.filter(user = request.user)
    if request.method == "POST":
        final_data = []
        selected_standard = request.POST.get('selected_standard')
        filtered_subject = subject.objects.filter(user = request.user).filter(standard = selected_standard)
        for i in filtered_subject:
            income_data = income_details.objects.filter(subject = i)   
            for j in income_data:
                final_data.append(j)

        return render(request,"standardwise_income.html",{'final_data':final_data,})


    return render(request,"standardwise_income.html",{'standard_list':standard_list})


@login_required
def subjectwise_income(request):
    subject_list = subject.objects.filter(user = request.user)
    if request.method =="POST":
        subject_list = subject.objects.filter(user = request.user)
        final_data = []
        selected_subject = request.POST.get("selected_subject")
        income_data = income_details.objects.filter(subject = selected_subject)
        for j in income_data:
            final_data.append(j)
        return render(request,"subjectwise_income.html",{'final_data':final_data,'subject_list':subject_list})



    return render(request,"subjectwise_income.html",{'subject_list':subject_list})


@login_required
def datewise_income(request):
    final_data = []
    if request.method =="POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        final_data = income_details.objects.filter(income_date__range = [start_date,end_date])
        
        return render(request,"datewise_income.html",{'final_data':final_data})


    return render(request,"datewise_income.html")

