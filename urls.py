"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from rest import views
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'department', views.DepartmentViewSet)
router.register(r'resourceDefined', views.ResourceDefinedViewSet)
router.register(r'attributeDefined', views.AttributeDefinedViewSet)
router.register(r'resource/label', views.LabelKeyViewSet, basename='rs-labels-k')
router.register(r'resource/label/(?P<label_k>[^/.]*)', views.LabelValueViewSet, basename='rs-labels-v')
router.register(r'(?P<resource_defined>[^/.]+)', views.ResourceViewSet, basename='rs')

urlpatterns = [
    path(r'v1/login/', views.CustomAuthToken.as_view()),
    path(r'v1/mine/', views.MineViewSet.as_view(), name="mine"),
    path('v1/', include(router.urls)),
    path('docs', include_docs_urls(title="CMDB API DOC")),
]
