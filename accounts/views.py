from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from contacts.models import Contact
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import requests #for the weather api
import ipinfo #for auto geolocation from IP: longtitude and latitude

def register(request): #If POST, then register user and redirect, otherwise render template
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Check for new username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    # Looks good
                    user = User.objects.create_user(
                        username=username, 
                        password=password, 
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    #Login after register
                    #auth.login(request, user)
                    #messages.success(request, 'You are now logged in')
                    #return redirect('index')
                    
                    #redirect to login page to login for first time
                    user.is_active = True
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    # Send welcome email
                    # email_subject = 'Welcome to KT Real Estate!'
                    # email_message = 'Thank you for registering in KT Real Estate. Login here: "www.try.com" '
                    # email_from = settings.EMAIL_HOST_USER
                    # recipient_list = [user.email, 'ktstoch@gmail.com']
                    # send_mail(email_subject, email_message, email_from, recipient_list, fail_silently=False)
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('index')

def dashboard(request):
    user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)
    now = datetime.today()
    access_token = '5024d30287db10' #from ipinfo
    handler = ipinfo.getHandler(access_token) #from ipinfo
    details = handler.getDetails() #from ipinfo
    coordinates =details.loc #from ipinfo
    #details.city used because it gets the city and not the specific area i think
    params = {
    'access_key': '74a4786f2e4c1777256fa4a241d40a69',
    'query': coordinates,
    } #from weatherstack
    api_result = requests.get('http://api.weatherstack.com/current', params) #from weatherstack
    api_response = api_result.json() #from weatherstack
    weather = u'Current temperature in %s is %d℃' % (details.city, api_response['current']['temperature']) #from weatherstack
    
    context = {
        'contacts': user_contacts,
        'time': now,
        'weather': weather,
    }
    return render(request, 'accounts/dashboard.html', context)
    #in this function u get the coordinates(longtitude,latitude) from IP via ipinfo 50k calls, and then use them in weatherstack params (250 calls per month) to get weather for specific location
    #OLD version of query weather = u'Current temperature in %s is %d℃' % (api_response['location']['name'], api_response['current']['temperature']) #from weatherstack