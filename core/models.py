from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
# from django.contrib.auth.models import AbstractUser




class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    email = models.EmailField(unique=True)  # Add this line to enforce unique emails

    ##
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
    

    

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='public')
    location = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='event_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    attendee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Ticket for {self.event.title} - {self.attendee.username}"
    
class JobApplication(models.Model):
    position = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    portfolio = models.URLField(blank=True, null=True)
    cover_letter = models.TextField()
    start_date = models.DateField()
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full-time'),
            ('part_time', 'Part-time'),
            ('contract', 'Contract/Freelance'),
            ('internship', 'Internship')
        ]
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('received', 'Received'),
            ('reviewing', 'Reviewing'),
            ('interview', 'Interview'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired')
        ],
        default='received'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"


