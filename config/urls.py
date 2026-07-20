from django.urls import include, path
from django.views.generic import RedirectView

from catalog.auth_views import ShelterLoginView

# Hard URL so path kwargs from /admin/... are not passed into reverse()
_manage_redirect = RedirectView.as_view(url="/manage/", permanent=False)

urlpatterns = [
    # Staff manage panel (site-styled CRUD)
    path("manage/", include("catalog.staff_urls")),
    # Legacy Django Admin UI hidden → /manage/
    path("admin/", _manage_redirect, name="admin_redirect"),
    path("admin/<path:unused>/", _manage_redirect, name="admin_redirect_subpath"),
    # Custom login: staff → manage, readers → site
    path("accounts/login/", ShelterLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("catalog.api_urls")),
    path("", include("catalog.urls")),
]
