from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Django's own admin login page is used at /admin/.
# Only accounts with is_staff=True can log in there. Police accounts are created
# with is_staff=False, so they cannot access the admin panel.


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
