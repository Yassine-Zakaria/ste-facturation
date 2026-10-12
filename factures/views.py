import datetime
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import ContactForm, FactureForm
from .models import Facture

AGENT_GROUP_NAME = 'Agents de collecte'


def is_admin(user):
    return user.is_authenticated and user.is_staff


def is_agent(user):
    return user.is_authenticated and user.groups.filter(name=AGENT_GROUP_NAME).exists()


def is_client(user):
    return user.is_authenticated and not user.is_staff and not is_agent(user)


def is_admin_or_agent(user):
    return user.is_authenticated and (user.is_staff or is_agent(user))


class ClientAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d’utilisateur'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})


class AdminAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d’utilisateur'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})


class AgentAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d’utilisateur'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})


class ClientLoginView(LoginView):
    template_name = 'factures/login_client.html'
    form_class = ClientAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('client_space')

    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff:
            messages.error(self.request, 'Ce compte est réservé aux administrateurs.')
            return self.form_invalid(form)
        return super().form_valid(form)


class AdminLoginView(LoginView):
    template_name = 'factures/login_admin.html'
    form_class = AdminAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff and not user.is_superuser:
            messages.error(self.request, 'Ce compte n\'est pas autorisé pour l\'administration.')
            return self.form_invalid(form)
        return super().form_valid(form)


class AgentLoginView(LoginView):
    template_name = 'factures/login_agent.html'
    form_class = AgentAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('agent_space')

    def form_valid(self, form):
        user = form.get_user()
        if not is_agent(user):
            messages.error(self.request, 'Ce compte n\'est pas autorisé à la collecte des données clients.')
            return self.form_invalid(form)
        return super().form_valid(form)


def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_staff:
        return redirect('dashboard')
    if is_agent(request.user):
        return redirect('agent_space')
    return redirect('client_space')


def home(request):
    return render(request, 'factures/home.html')


def _build_pdf_report(lines):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle('STE - Rapport administratif')
    pdf.setFont('Helvetica', 11)

    y = 780
    for line in lines[:30]:
        pdf.drawString(50, y, str(line))
        y -= 18

    pdf.save()
    return buffer.getvalue()


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            subject = f"Nouveau message - {form.cleaned_data['objet']}"
            body = (
                f"Nom: {form.cleaned_data['nom']}\n"
                f"Email: {form.cleaned_data['email']}\n"
                f"Téléphone: {form.cleaned_data['telephone'] or 'Non renseigné'}\n"
                f"Objet: {form.cleaned_data['objet']}\n\n"
                f"Message:\n{form.cleaned_data['message']}"
            )
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [getattr(settings, 'STE_ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)],
                fail_silently=False,
            )
            messages.success(request, 'Votre message a bien été envoyé. Notre équipe vous répondra rapidement.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'factures/contact.html', {'form': form})


def login_choice(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        if is_agent(request.user):
            return redirect('agent_space')
        return redirect('client_space')
    return render(request, 'factures/login_choice.html')


@login_required(login_url='login')
@user_passes_test(is_agent, login_url='login')
def agent_space(request):
    return render(request, 'factures/agent_space.html', {'user': request.user})


@login_required(login_url='login')
@user_passes_test(is_client, login_url='login')
def client_space(request):
    return render(request, 'factures/client_space.html', {'user': request.user})


class FactureList(ListView):
    model = Facture
    template_name = 'factures/liste.html'

    @method_decorator(login_required(login_url='login'))
    @method_decorator(user_passes_test(is_admin_or_agent, login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            return Facture.objects.filter(
                Q(numero_facture__icontains=q)
                | Q(matricule_client__icontains=q)
                | Q(nom_client__icontains=q)
                | Q(quartier__icontains=q)
            )
        return Facture.objects.all()


class FactureCreate(CreateView):
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form.html'
    success_url = reverse_lazy('liste_factures')

    @method_decorator(login_required(login_url='login'))
    @method_decorator(user_passes_test(is_admin_or_agent, login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FactureUpdate(UpdateView):
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form.html'
    success_url = reverse_lazy('liste_factures')

    @method_decorator(login_required(login_url='login'))
    @method_decorator(user_passes_test(is_admin_or_agent, login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FactureDelete(DeleteView):
    model = Facture
    template_name = 'factures/confirm_delete.html'
    success_url = reverse_lazy('liste_factures')

    @method_decorator(login_required(login_url='login'))
    @method_decorator(user_passes_test(is_admin, login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FacturePrint(DetailView):
    model = Facture
    template_name = 'factures/print.html'

    @method_decorator(login_required(login_url='login'))
    @method_decorator(user_passes_test(is_admin, login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def dashboard(request):
    total_factures = Facture.objects.count()
    total_encaisse = Facture.objects.aggregate(Sum('net_a_payer'))['net_a_payer__sum'] or 0
    conso_moyenne = Facture.objects.aggregate(Avg('conso'))['conso__avg'] or 0

    context = {
        'total_factures': total_factures,
        'total_encaisse': total_encaisse,
        'conso_moyenne': round(conso_moyenne, 2),
    }
    return render(request, 'factures/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def export_report_pdf(request):
    factures = Facture.objects.order_by('-date_facture')[:15]
    total_factures = Facture.objects.count()
    total_encaisse = Facture.objects.aggregate(Sum('net_a_payer'))['net_a_payer__sum'] or 0
    consommation_totale = Facture.objects.aggregate(Sum('conso'))['conso__sum'] or 0

    lines = [
        'STE - Rapport administratif',
        f"Date d’édition: {datetime.date.today().strftime('%d/%m/%Y')}",
        f"Factures enregistrées: {total_factures}",
        f"Montant total encaissé: {total_encaisse} FCFA",
        f"Consommation totale: {consommation_totale} m³",
        '---',
    ]

    for facture in factures:
        lines.append(
            f"{facture.numero_facture} | {facture.nom_client} | {facture.quartier} | "
            f"{facture.net_a_payer} FCFA | {facture.statut_paiement}"
        )

    pdf_content = _build_pdf_report(lines)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ste_rapport_admin.pdf"'
    return response


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def paiement(request):
    total_factures = Facture.objects.count()
    total_encaisse = Facture.objects.aggregate(Sum('net_a_payer'))['net_a_payer__sum'] or 0
    moyenne_facture = Facture.objects.aggregate(Avg('net_a_payer'))['net_a_payer__avg'] or 0
    meilleurs_clients = Facture.objects.order_by('-net_a_payer')[:5]
    status_summary = list(
        Facture.objects.values('statut_paiement').annotate(count=Count('id')).order_by('statut_paiement')
    )

    status_labels = []
    status_values = []
    status_mapping = {
        'en_attente': 'En attente',
        'paye': 'Payé',
        'partiel': 'Partiel',
        'impaye': 'Impayé',
    }

    for item in status_summary:
        status_labels.append(status_mapping.get(item['statut_paiement'], item['statut_paiement']))
        status_values.append(item['count'])

    context = {
        'total_factures': total_factures,
        'total_encaisse': total_encaisse,
        'moyenne_facture': round(moyenne_facture, 2),
        'meilleurs_clients': meilleurs_clients,
        'status_summary': status_summary,
        'status_labels': status_labels,
        'status_values': status_values,
    }
    return render(request, 'factures/paiements.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def recherche_factures(request):
    query = request.GET.get('q', '').strip()
    if query:
        results = Facture.objects.filter(
            Q(numero_facture__icontains=query)
            | Q(matricule_client__icontains=query)
            | Q(nom_client__icontains=query)
            | Q(quartier__icontains=query)
            | Q(numero_quartier__icontains=query)
        ).order_by('-date_facture')
    else:
        results = Facture.objects.none()

    context = {
        'query': query,
        'results': results,
        'count': results.count(),
    }
    return render(request, 'factures/search.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def statistiques_avancees(request):
    total_encaisse = Facture.objects.aggregate(Sum('net_a_payer'))['net_a_payer__sum'] or 0
    consommation_totale = Facture.objects.aggregate(Sum('conso'))['conso__sum'] or 0
    moyenne_consommation = Facture.objects.aggregate(Avg('conso'))['conso__avg'] or 0

    par_quartier = Facture.objects.values('quartier').annotate(
        total = Sum('net_a_payer'),
        clients = Count('id'),
    ).order_by('-total')

    par_mois = Facture.objects.values('mois').annotate(
        total = Sum('net_a_payer'),
        volume = Sum('conso'),
    ).order_by('-total')[:6]

    quartier_labels = [item['quartier'] for item in par_quartier]
    quartier_values = [float(item['total']) for item in par_quartier]
    mois_labels = [item['mois'] for item in par_mois]
    mois_values = [float(item['total']) for item in par_mois]

    context = {
        'total_encaisse': total_encaisse,
        'consommation_totale': consommation_totale,
        'moyenne_consommation': round(moyenne_consommation, 2),
        'par_quartier': par_quartier,
        'par_mois': par_mois,
        'quartier_labels': quartier_labels,
        'quartier_values': quartier_values,
        'mois_labels': mois_labels,
        'mois_values': mois_values,
    }
    return render(request, 'factures/statistiques.html', context)

