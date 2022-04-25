from django.urls import path, include
from . import views

from rest_framework import routers
from rest_framework.authtoken import views as drf_views

router = routers.DefaultRouter()
router.register(r'charts', views.ChartViewSet, 'charts')
router.register(r'colorencodings', views.ColorEncodingViewSet, 'colorencodings')
router.register(r'rangecolors', views.RangeColorViewSet, 'rangecolors')
router.register(r'datasets', views.DatasetViewSet, 'datasets')
router.register(r'colors', views.ColorViewSet, 'colors')
router.register(r'colorschemes', views.ColorSchemeViewSet, 'colorschemes')
router.register(r'colorconfig', views.ColorConfigViewSet, 'colorconfig')
router.register(r'parameters', views.ParameterViewSet, 'parameters')
router.register(r'examples', views.ExampleViewSet, 'examples')
router.register(r'mvcolorencodings', views.MVColorEncodingViewSet, 'mvcolorencodings')
router.register(r'mvconceptgroupings', views.MVConceptGroupingViewSet, 'mvconceptgroupings')

# router.register(r'auth', drf_views.obtain_auth_token, 'auth')
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]