"""
URL configuration for besales project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from rest_framework.routers import DefaultRouter
from gettoken.views import TokenViewSet
from master.views import JenisBahanViewSet

from django.contrib import admin
from django.urls import path, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Konfigurasi Schema Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Sales Entry API",
        default_version="v1",
        description="Dokumentasi API untuk Sales Entry",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@salesentry.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# router = DefaultRouter()
# router.register(r'api/token', TokenViewSet, basename='token')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger UI
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # Redoc (Alternatif dokumentasi API)
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

  #  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  #  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', TokenViewSet.as_view({'post': 'create'}), name='token'),

    # Master Jenis Bahan
    path('api/jenisbahan/list/', JenisBahanViewSet.as_view({'get': 'list'}), name='list_jenisbahan'),
    path('api/jenisbahan/create/', JenisBahanViewSet.as_view({'post': 'create'}), name='create_jenisbahan'),
    path('api/jenisbahan/<int:pk>/', JenisBahanViewSet.as_view({'get': 'retrieve'}), name='retrieve_jenisbahan'),
    path('api/jenisbahan/<int:pk>/update/', JenisBahanViewSet.as_view({'put': 'update'}), name='update_jenisbahan'),
    path('api/jenisbahan/<int:pk>/delete/', JenisBahanViewSet.as_view({'put': 'destroy'}), name='delete_jenisbahan'),  

    # path('api/jenisbahan/retrieve/', TokenViewSet.as_view({'get': 'retrieve'}), name='retrieve_jenisbahan'),
    # path('api/jenisbahan/update/', TokenViewSet.as_view({'put': 'update'}), name='update_jenisbahan'),
    # path('api/jenisbahan/delete/', TokenViewSet.as_view({'put': 'delete'}), name='delete_jenisbahan'),
] # + router.urls
