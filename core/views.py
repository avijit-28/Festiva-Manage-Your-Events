# core/views.py
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, Category, Ticket
from .forms import EventForm
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend

from django.utils.encoding import force_str
from django.contrib.auth import login, authenticate

from django.core.mail import EmailMultiAlternatives 
from .models import JobApplication
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import json


# from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_pending_approvals(request):
    User = get_user_model()
    pending_admins = User.objects.filter(role='admin', is_approved=False)
    return render(request, 'controller/pending_approvals.html', {
        'pending_admins': pending_admins
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_admin(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_approved = True
        user.save()
        
        # Send approval email
        subject = 'Your Admin Account Has Been Approved'
        text_content = f"""Hello {user.first_name},
        Your admin account for Festiva has been approved.
        You can now log in at: http://127.0.0.1:8000/login"""
        html_content = render_to_string('emails/admin_approved.html', {
            'user': user,
            'login_url': request.build_absolute_uri(reverse('login'))})

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(
            
        )
        messages.success(request, f'Admin {user.email} has been approved')
        return redirect('admin_pending_approvals')
    
    return render(request, 'controller/confirm_approval.html', {'user': user})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def pending_approvals(request):
    return render(request, 'controller/pending_approvals.html')


def home(request):
    featured_events = Event.objects.filter(event_type='public').order_by('-created_at')[:6]
    return render(request, 'home.html', {'featured_events': featured_events})

@login_required
def browse_events(request):
    events = Event.objects.filter(event_type='public').order_by('-start_date')
    categories = Category.objects.all()
    return render(request, 'browse_events.html', {'events': events, 'categories': categories})

@login_required
def create_event(request):
    categories = Category.objects.all()  # Get all categories first
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()  # Initialize empty form for GET requests
    
    return render(request, 'create_event.html', {
        'form': form,
        'categories': categories
    })
def customize_view(request):
    package = request.GET.get('package')

    # Mapping package names to their corresponding template files
    package_templates = {
        'royal_wedding': 'customization/Customize Royal Wedding.html',
        'classic_wedding': 'customization/Customize Classic Wedding.html',
        'intimate_wedding': 'customization/Customize Intimate Wedding.html',
        'executive_summit': 'customization/Customize Executive Summit.html',
        'business_conference': 'customization/Customize Business Conference.html',
        'team_workshop': 'customization/Customize Team Workshop.html',
        'grand_annaprasana': 'customization/Customize Grand Annaprasana.html',
        'grand_celebration': 'customization/Customize Grand Celebration.html',
        'kids_party': 'customization/Customize Kids Party.html',
        'international_conference': 'customization/Customize International Conference.html',
        'professional_seminar': 'customization/Customize Professional Seminar.html',
        'workshop': 'customization/Customize Workshop.html',
        'traditional_ceremony': 'customization/Customize Traditional Ceremony.html',
        'simple_blessing': 'customization/Customize Simple Blessing.html',
        'stadium_concert': 'customization/Customize Stadium Concert.html',
        'concert_hall_event': 'customization/Customize Concert Hall Event.html',
        'club_performance': 'customization/Customize Club Performence.html',

    }

    template_path = package_templates.get(package)

    if template_path:
        return render(request, template_path, {'package': package})
    else:
        return HttpResponse("Invalid package type.", status=404)

def chatbot_page(request):
    return render(request, 'chat3.html') 

def get_chat_response(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            message = data.get('msg', '')
            menu = data.get('menu', 'main')
            session_id = data.get('session_id', '')
            
            # Here you would typically process the message and generate a response
            # For now, we'll just echo back a simple response
            response = {
                'response': f"I received your message: '{message}'",
                'menu': menu,
                'options': [
                    {'id': 'option1', 'text': 'Option 1'},
                    {'id': 'option2', 'text': 'Option 2'}
                ]
            }
            return JsonResponse(response)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_organizer = request.user == event.organizer
    has_ticket = Ticket.objects.filter(event=event, attendee=request.user).exists()
    
    return render(request, 'event_detail.html', {
        'event': event,
        'is_organizer': is_organizer,
        'has_ticket': has_ticket
    })

@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = event.price * quantity
        
        # Create ticket
        Ticket.objects.create(
            event=event,
            attendee=request.user,
            quantity=quantity,
            total_price=total_price
        )
        
        messages.success(request, 'Ticket booked successfully!')
        return redirect('dashboard')
    
    return render(request, 'book_ticket.html', {'event': event})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'delete_event.html', {'event': event})

@login_required
def dashboard(request):
    if request.user.role == 'organizer':
        events = request.user.organized_events.all()
        tickets_sold = Ticket.objects.filter(event__in=events).count()
    else:
        events = []
        tickets_sold = 0
        
    upcoming_events = request.user.tickets.select_related('event').filter(
        event__start_date__gte=timezone.now()
    ).order_by('event__start_date')
    
    return render(request, 'dashboard.html', {
        'events': events,
        'tickets_sold': tickets_sold,
        'upcoming_events': upcoming_events
    })

def profile(request):
    return render(request, 'profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.bio = request.POST.get('bio')

        if user.role == 'organizer':
            user.organization_name = request.POST.get('organization_name')
            user.website = request.POST.get('website')
            user.tax_id = request.POST.get('tax_id')

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        if 'remove_profile_picture' in request.POST:
            user.profile_picture = None

        user.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')

    return render(request, 'edit_profile.html')

def acc_settings(request):
    return render(request, 'acc_settings.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

def login_view(request):
     if request.method == 'POST':
        username = request.POST.get('username')  # This is actually the email
        password = request.POST.get('password')
        
        # Validate inputs
        if not username or not password:
            messages.error(request, 'Please provide both email and password')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Account not activated. Please check your email.')
        else:
            messages.error(request, 'Invalid email or password')
    
     return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        # Generate username from email
        username = email.split('@')[0]
        while User.objects.filter(username=username).exists():
            username = f"{email.split('@')[0]}"
        
        # Create the user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password1),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            is_active=False,
            role=user_type,
        )

        # Handle special fields
        if user_type == 'organizer':
            user.is_organizer = True
            user.organization_name = request.POST.get('organization_name', '')
            user.website = request.POST.get('website', '')
            user.tax_id = request.POST.get('tax_id', '')
        elif user_type == 'admin':
            user.is_staff = True
            user.is_superuser = False
        
        user.save()

        # Send verification email ONLY for attendees
        if user_type == 'user':
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Verify Your Festiva Account'
            message = render_to_string('emails/verify_email.html', {
                'user': user,
                'verification_url': verification_url,
            })

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    html_message=message,
                    fail_silently=False
                )
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
            except Exception as e:
                messages.error(request, f"Failed to send verification email: {str(e)}")
        else:
            messages.success(request, 'Registration successful! Please wait for admin approval.')

        return redirect('login')
    else:
        return render(request, 'register.html')

@login_required
def blog(request):
    return render(request, 'blog.html')

@login_required
def testimonials(request):     
    return render(request, 'testimonials.html')

# Information page views
@login_required
def pricing(request):
    return render(request, 'pricing.html')

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def team(request):
    return render(request, 'team.html')

# @login_required
def careers(request):
    return render(request, 'careers.html')

# @login_required
def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        full_message = f"Message from {name} ({email}):\n\n{message}"

        send_mail(subject, full_message, settings.DEFAULT_FROM_EMAIL, ['youremail@example.com'])

        messages.success(request, 'Your message has been sent!')
    
    return render(request, 'contact.html')



def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user, backend=backend)
        messages.success(request, 'Your email has been verified! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('home')

# Support page views
def faq(request):
    return render(request, 'faq.html')

def help(request):
    return render(request, 'help.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

@login_required
def apply_now(request):
    if request.method == 'POST':
        try:
            # Create and save application
            application = JobApplication(
                position=request.POST.get('position', 'General Application'),
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                resume=request.FILES['resume'],
                portfolio=request.POST.get('portfolio', ''),
                cover_letter=request.POST['cover_letter'],
                start_date=request.POST['start_date'],
                employment_type=request.POST['employment_type']
            )
            application.save()

            # Email to applicant
            applicant_subject = f"Application Received for {application.position}"
            applicant_message = render_to_string('emails/application_received_applicant.html', {
                'application': application
            })
            
            send_mail(
                applicant_subject,
                applicant_message,
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                html_message=applicant_message,
                fail_silently=False
            )

            # Email to HR
            hr_subject = f"New Application: {application.position}"
            hr_message = render_to_string('emails/application_received_hr.html', {
                'application': application
            })
            
            send_mail(
                hr_subject,
                hr_message,
                settings.DEFAULT_FROM_EMAIL,
                ['hr@festiva.com', 'careers@festiva.com'],  # Your HR emails
                html_message=hr_message,
                fail_silently=False
            )

            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('careers')

        except Exception as e:
            messages.error(request, f'There was an error submitting your application: {str(e)}')
            return redirect('apply_now')

    return render(request, 'apply_now.html')

@login_required
def team(request):
    # Sample data - replace with your actual team data or database queries
    context = {
        'dev_team': [
            {'name': 'Taylor Kim', 'role': 'Senior Developer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Jordan Smith', 'role': 'Backend Engineer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Casey Wong', 'role': 'Frontend Developer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Riley Patel', 'role': 'Mobile Developer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Morgan Lee', 'role': 'DevOps Engineer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Jamie Chen', 'role': 'QA Specialist', 'image': 'https://via.placeholder.com/150'},
        ],
        'design_team': [
            {'name': 'Sydney Park', 'role': 'UX Designer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Drew Wilson', 'role': 'UI Designer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Blake Martin', 'role': 'Graphic Designer', 'image': 'https://via.placeholder.com/150'},
            {'name': 'Taylor Kim', 'role': 'Motion Designer', 'image': 'https://via.placeholder.com/150'},
        ],
        'event_managers': [
            {
                'name': 'Chris Johnson',
                'role': 'Senior Event Manager',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Specializes in corporate events and conferences'
            },
            {
                'name': 'Maria Garcia',
                'role': 'Wedding Specialist',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Creates magical wedding experiences'
            },
            {
                'name': 'David Kim',
                'role': 'Music Festival Director',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Lives and breathes festival culture'
            }
        ],
        'support_team': [
            {
                'name': 'Emma Wilson',
                'role': 'Customer Support Lead',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Ensures every customer has an exceptional experience',
                'expertise': ['Technical Support', 'Account Management', 'Training'],
                'languages': ['English', 'Spanish', 'French']
            },
            {
                'name': 'Raj Patel',
                'role': 'Technical Support Specialist',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Solves technical challenges with a smile',
                'expertise': ['Platform Troubleshooting', 'API Support', 'Integrations'],
                'languages': ['English', 'Hindi']
            },
            {
                'name': 'Sophie Martin',
                'role': 'Event Support Coordinator',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Makes sure every event runs smoothly',
                'expertise': ['On-site Support', 'Vendor Coordination', 'Logistics'],
                'languages': ['English', 'German']
            }
        ],
        'partner_team': [
            {
                'name': 'Michael Chen',
                'role': 'Director of Partnerships',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Builds strategic relationships with top vendors',
                'specialties': ['Venues', 'Catering', 'AV Equipment'],
                'region': 'North America'
            },
            {
                'name': 'Aisha Johnson',
                'role': 'Partner Success Manager',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Ensures our partners have everything they need',
                'specialties': ['Entertainment', 'Decor', 'Staffing'],
                'region': 'Europe'
            },
            {
                'name': 'Diego Rodriguez',
                'role': 'Vendor Relations Specialist',
                'image': 'https://via.placeholder.com/300',
                'bio': 'Connects clients with perfect vendors',
                'specialties': ['Photography', 'Transportation', 'Security'],
                'region': 'Latin America'
            }
        ]
    }
    return render(request, 'team.html', context)
