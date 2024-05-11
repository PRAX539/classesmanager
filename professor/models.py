from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

method_of_payment =(
        ('Not Applicable','Not Applicable'),
        ('fixed per month','fixed per month'),
        ('fixed per Year','fixed per Year'),
        ('lecturewise','lecturewise'),
        ('hourwise','hourwise'),
       

    )
genders = (
    ('Male','Male'),
    ('Female','Female'),
    ('Others','Others')
)
class CustomUser(AbstractUser):
    middle_name = models.CharField(blank = True, null = True, max_length = 100)
    contact_number = models.IntegerField(blank = True, null  =True)

    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"
    
    

class additional_data(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to = 'uploaded_images', blank = True, null = True)
    gender = models.CharField(choices=genders, max_length=10, default="Male")
    dob = models.DateField(blank = True, null = True)
    address = models.TextField(blank = True, null = True)
    city = models.CharField(max_length=100,blank = True, null = True)
    state = models.CharField(max_length=100,blank = True, null = True)
    country = models.CharField(max_length=100, blank  = True, null = True)
    pincode = models.IntegerField(blank = True, null = True)
    tags = models.TextField(blank = True, null = True)

    def __str__(self):
       return  self.user.username

    @receiver(post_save, sender=CustomUser)
    def create_additional_data(sender, instance, created, **kwargs):
        if created:
            additional_data.objects.create(user=instance)

    @receiver(post_save, sender=CustomUser)
    def save_additional_data(sender, instance, **kwargs):
        instance.additional_data.save()


class classes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    institute_name = models.CharField(max_length=100)
    institute_details = models.TextField(verbose_name="institute address", blank = True, null = True)
    institute_contact = models.IntegerField(blank=True, null=True)
    disabled = models.BooleanField(default = False)
   

    def __str__(self):
        return self.institute_name

class standard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    standard_name = models.CharField(max_length=100)
    disabled = models.BooleanField(default = False)

    def __str__(self):
        return self.standard_name



class subject(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    standard = models.ForeignKey(standard, on_delete=models.CASCADE)
    classes = models.ForeignKey(classes, on_delete=models.CASCADE)
    method_of_payment = models.CharField(max_length=100, choices=method_of_payment)
    number_field = models.CharField(max_length=100, verbose_name="amount/Percentage")
    disabled = models.BooleanField(default = False)

    def __str__(self):
        return f'{self.classes.institute_name} - {self.standard.standard_name} - {self.subject_name}'





class daily_schedule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(subject, on_delete=models.CASCADE)
    topic = models.TextField(null = True, blank = True)
    set_reminder = models.BooleanField(default=False)
    calculated = models.BooleanField(default=False)
    

    def __str__(self):
        return str(self.schedule_date)

class income_details(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(subject, on_delete=models.CASCADE)
    income_date = models.DateField()
    income_amount = models.IntegerField()
    income_description = models.TextField()
    receipt_date = models.DateField(blank = True, null = True)
    receipt_number = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return self.subject.classes.institute_name




    