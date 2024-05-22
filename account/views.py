from django.shortcuts import render, redirect
from.forms import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name =first_name, last_name = last_name, email = email, username = username,  password=password)
            user.phone_number = phone_number
            user.save()

            # User activation
            current_site = get_current_site(request)
            mail_subject = 'Please Verify mail'
            message= render_to_string('accounts/account_verificatoin_mail.html',{
                    'user' : user,
                    'domain':current_site,
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
            to_email= user
            send_mail = EmailMessage(mail_subject,message,to=[to_email])
            # SMTP configuraation required so printing link in terminal
            # send_mail.send()
            print(f'http://{current_site}/accounts/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}')

            # messages.success(request, "Registration successful.")

            return redirect('/accounts/login/?command=verification&email='+email)
        
    else:
        form = RegistrationForm()

    context = {
        'form' : form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id= _cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart = cart)

                    # Getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                        # Getting the cart item from user to access his product variation
                        cart_item = CartItem.objects.filter(user = user)

                        existing_variation_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            existing_variation_list.append(list(existing_variation))
                            id.append(item.id)

                        # product_variation=[1,2,3,5,8...]
                        # existing_variation_list=[4,2,8]
                        # Get the common Product variation in both the list
                        for pr in product_variation:
                            if pr in existing_variation_list:
                                index = existing_variation_list.index(pr)
                                item_id = id[index]
                                cart_item = CartItem.objects.get(id = item_id)
                                cart_item.quantity += 1
                                cart_item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'Login Successful')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.path(url).query()
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')

        else:
            messages.error(request,'Invalid Login Credentials !')
            return redirect('login')
        

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (ValueError,TypeError,OverflowError, Account.DoesNotExist):
        user =None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Cogartulation, Your account is verified')
        return redirect('login')
    else:
        messages.error(request, 'Invalid Link!')
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method=='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Sending mail for password reset
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message= render_to_string('accounts/reset_password_mail.html',{
                    'user' : user,
                    'domain':current_site,
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
            to_email= user
            send_mail = EmailMessage(mail_subject,message,to=[to_email])
            # SMTP configuraation required so printing link in terminal
            # send_mail.send()    
            print(f'http://{current_site}/accounts/resetpassword_validate/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}')

            messages.success(request, 'Reset mail has been sent to your email')
            return redirect('login')


        else:
            messages.error(request, "Account doesn't exist")
            return redirect('forgotPassword')


    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (ValueError,TypeError,OverflowError, Account.DoesNotExist):
        user =None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetPassword')
    
    else:
        messages.error(request, 'Your link is expired')
        return redirect('login')
    

def resetPassword(request):
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed successfully')
            return redirect('login')
         
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')

    else:
        return render(request, 'accounts/resetPassword.html')
        
