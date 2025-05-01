# core/urls.py
from django.urls import path,include
from . import views
# from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

urlpatterns = [

     path('controller/approvals/', views.admin_pending_approvals, name='admin_pending_approvals'),
    path('controller/approve/<int:user_id>/', views.approve_admin, name='approve_admin'),
    path('controller/pending-approval/', views.pending_approvals, name='pending_approval'),


    # Main pages
    path('', views.home, name='home'),
    path('events/', views.browse_events, name='browse_events'),
    path('create-event/', views.create_event, name='create_event'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('blog/', views.blog, name='blog'),
    path('testimonials/', views.testimonials, name='testimonials'),
    

    # event management
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    
    # User management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('acc_settings/', views.acc_settings, name='acc_settings'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify-email'),
    path('careers/apply/', views.apply_now, name='apply_now'),
    
    # Information pages
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('team/', views.team, name='team'),
    path('careers/', views.careers, name='careers'),
    path('contact/', views.contact, name='contact'),
    path('customize/', views.customize_view, name='customization'),
    
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('get_chat_response/', views.get_chat_response, name='get_chat_response'),
    
    # Support pages
    path('faq/', views.faq, name='faq'),
    path('help/', views.help, name='help'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),


    # add password reset URLs
    path('password_reset_form/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done'),
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),


    
]
