from django.contrib.auth.views import LoginView
from django.urls import reverse


class ShelterLoginView(LoginView):
    """
    Same login form for everyone.
    - Staff / superuser → manage panel
    - Regular reader → public site (or ?next= if present)
    """

    template_name = "registration/login.html"

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("staff:dashboard")
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return reverse("catalog:home")
