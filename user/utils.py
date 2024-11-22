from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import holidays

def get_holidays_for_month(year, month, country='US'):
    country_holidays = holidays.CountryHoliday(country, years=[year])
    monthly_holidays = {date: name for date, name in country_holidays.items() if date.month == month}
    return monthly_holidays



    ## send the verification otp to the user account
def sent_otp_by_email(email):
    subject = "Your account verification email.."
     # otp = random.randint(100000,999999)
    otp = 123456
    message = f"Your OTP for account verification is {otp}"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()



## send the forgot password otp
def reset_pass_otp_email(email):
    subject = "Your account verification email.."
    # otp = random.randint(100000,999999)
    otp = 987654
    message = f"Your OTP for forgot password is {otp}"
    email_from = settings.EMAIL_HOST_USER
    ## send the required dat and parameters in the send_email function
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    ## save the otp in the user table for verification
    user_obj.otp = otp
    ## make the user unverified
    user_obj.is_verified = False
    user_obj.save()

def send_registration_email(recipient_email, registration_link):
    try:
        subject = 'Complete your registration'
        from_email = settings.EMAIL_HOST_USER
        to = [recipient_email]

        text_content = f"Please click the following link to complete your registration: {registration_link}"
        
        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.send()
        print(f"Sending email to: {recipient_email}")
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

   

