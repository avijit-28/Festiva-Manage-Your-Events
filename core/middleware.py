# core/middleware.py
from django.shortcuts import redirect

class AdminApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (request.user.is_authenticated and 
            request.user.role == 'admin' and 
            not request.user.is_approved and
            not request.path.startswith('/pending-approval/')):
            return redirect('pending_approval')
        return None