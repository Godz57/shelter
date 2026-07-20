from django.urls import include, path
from django.views.generic import RedirectView

# Hard URL so path kwargs from /admin/... are not passed into reverse()
_manage_redirect = RedirectView.as_view(url="/manage/", permanent=False)

urlpatterns = [
    # Staff manage panel (site-styled CRUD) — primary admin UX
    path("manage/", include("catalog.staff_urls")),
    # Legacy Django Admin UI hidden: everything under /admin/ → /manage/
    path("admin/", _manage_redirect, name="admin_redirect"),
    path("admin/<path:unused>/", _manage_redirect, name="admin_redirect_subpath"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("catalog.api_urls")),
    path("", include("catalog.urls")),
]
