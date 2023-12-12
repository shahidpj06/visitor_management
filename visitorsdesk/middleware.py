from .models import Company

class SetDefaultCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.company:
            # Set a default company for the user
            # You might want to implement this logic based on your requirements
            default_company = Company.objects.first()
            if default_company:
                request.user.company = default_company
                request.user.save()

        response = self.get_response(request)
        return response