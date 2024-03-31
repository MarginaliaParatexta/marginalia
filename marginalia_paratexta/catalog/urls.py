from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('creations/', views.ProductListView.as_view(), name='creations'),
    path('knots/', views.KnotListView.as_view(), name='knots'),
    path('graph/', views.grafico_barras_view, name='graph'),
    path('map/', views.world_map_view, name='map'),
    path('wordcloud/', views.word_cloud, name='wordcloud'),
    re_path(r'^creation/(?P<pk>[0-9a-f-]+)$', views.product_detail_view, name='creation-detail'),
    re_path(r'^knot/(?P<pk>[0-9a-f-]+)$', views.knot_detail_view, name='knot-detail'),
    path('country/<str:country_iso>/creations/formato/<str:formatos>/', views.country_creations_list_formato, name='country_creations_list_formato'),
    path('country/<str:country_iso>/creations/<str:query_for>/keyWord/<str:keyWords>/', views.country_creations_list_keyWord, name='country_creations_list_keyWord'),
    path('country/<str:country_iso>/creations/<str:query_for>/<str:formatos>/<str:keywords>/', views.country_creations_list, name='country_creations_list'),
    path('country/<str:country_iso>/creations/', views.country_creations_list, name='country_creations_list'),
    path('year/<int:year>/<int:year_range>/<str:query_for>/creations/', views.year_creations_list, name='year_creations_list'),
    path('year/<int:year>/<int:year_range>/<str:query_for>/creations/<str:filter1>/', views.year_creations_list, name='year_creations_list'),
    path('year/<int:year>/<int:year_range>/<str:query_for>/creations/<str:filter1>/<str:filter2>/', views.year_creations_list, name='year_creations_list'),
    path('year/<int:year>/<int:year_range>/<str:query_for>/creations/<str:filter1>/<str:filter2>/<str:filter3>/', views.year_creations_list, name='year_creations_list'),
    path('year/<int:year>/<int:year_range>/<str:query_for>/creations/<str:filter1>/<str:filter2>/<str:filter3>/<str:filter4>/', views.year_creations_list, name='year_creations_list'),
    path('recuperar-contraseña/', views.recuperar_contraseña_form, name='recuperar_contraseña_form'),
    path('recuperar-contraseña/procesar/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('contraseña-enviada/', views.contraseña_enviada, name='contraseña_enviada'),
    path('correo-invalido/', views.correo_invalido, name='correo_invalido'),
]
