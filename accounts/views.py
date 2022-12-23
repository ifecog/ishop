from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .models import Account
from django.contrib.auth.decorators import login_required

# shopcart
from cart.models import Cart, CartItem
from cart.views import _cart_id

# verification emails
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from ishop import settings
# from django.http import HttpResponse

# Create your views here.


def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        phonenumber = request.POST['phonenumber']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirmpassword']

        if password == confirm_password:
            if Account.objects.filter(username=username).exists():
                messages.error(request, 'username already taken')
                return redirect('signup')
            else:
                if Account.objects.filter(email=email).exists():
                    messages.error(request, 'email already used')
                    return redirect('signup')
                else:
                    user = Account.objects.create_user(
                        first_name=firstname, last_name=lastname, email=email, username=username, password=password)
                    user.phone_number = phonenumber
                    auth.login(request, user)
                    messages.success(request, 'Signup Successful!')
                    user.save()

                    # user activation
                    current_site = get_current_site(request)
                    email_subject = 'iShop Account Activation',
                    message = render_to_string('accounts/account_verification_email.html', {
                        'user': user,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user)
                    })
                    from_email = settings.EMAIL_HOST_USER
                    recipient = [email]
                    send_email = EmailMessage(
                        email_subject, message, from_email, recipient)
                    send_email.send(fail_silently=False)

                    # Alternate method using send_mail function
                    # subject = 'This is a mail from IfeCog'
                    # message = f'hi {firstname}, this mail is about your registration'
                    # from_email = settings.EMAIL_HOST_USER
                    # recipient_list = [email]
                    # send_mail(subject, message, from_email,
                    #           recipient_list, fail_silently=False)

                    # messages.success(
                    #     request, 'Thank you for signing up with us. Check your email inbox to verify your account')
                    return redirect('/accounts/login/?command=verification&email='+email)

        else:
            messages.error(request, 'passwords do not match')
            return redirect('signup')

    return render(request, 'accounts/signup.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                print("try block")
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()
                print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    print(cart_item)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                print("except block")
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')

        else:
            messages.error(
                request, 'Incorrect email, try again!')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are successfully logged out')
        return redirect('home')

    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Conratulations! Your account has been activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # forgot password reset
            current_site = get_current_site(request)
            email_subject = 'Reset your Password',
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            from_email = settings.EMAIL_HOST_USER
            recipient = [email]
            send_email = EmailMessage(
                email_subject, message, from_email, recipient)
            send_email.send(fail_silently=False)

            messages.success(
                request, "Password reset email has been sent to your email")
            return redirect('login')

        else:
            messages.error(
                request, "There is no user with this email. Please, correct email")
            return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(
            request, 'Please reset your password')
        return redirect('password_reset')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('forgotpassword')


def password_reset(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password Reset Successful!")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match. Try again")
            return redirect('password_reset')

    return render(request, 'accounts/password_reset.html')
