from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rapport/pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('paiements/', views.paiement, name='paiements'),
    path('recherche/', views.recherche_factures, name='recherche_factures'),
    path('statistiques/', views.statistiques_avancees, name='statistiques_avancees'),
    path('login/', views.login_choice, name='login'),
    path('login/client/', views.ClientLoginView.as_view(), name='client_login'),
    path('login/agent/', views.AgentLoginView.as_view(), name='agent_login'),
    path('login/admin/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('agent/', views.agent_space, name='agent_space'),
    path('client/', views.client_space, name='client_space'),
    path('factures/', views.FactureList.as_view(), name='liste_factures'),
    path('ajouter/', views.FactureCreate.as_view(), name='ajouter'),
    path('modifier/<int:pk>/', views.FactureUpdate.as_view(), name='modifier'),
    path('supprimer/<int:pk>/', views.FactureDelete.as_view(), name='supprimer'),
    path('imprimer/<int:pk>/', views.FacturePrint.as_view(), name='imprimer'),
]
