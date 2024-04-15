from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ricept.urls')),
    path('api/', include('djoser.urls')),  # Работа с пользователями
    path('api/auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]
