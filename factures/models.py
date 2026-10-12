import datetime

from django.db import models

from .services import (
    calculate_total_with_fees,
    calculate_usage_amount,
    generate_client_matricule,
    generate_invoice_number,
)


class Facture(models.Model):
    QUARTIER_CHOICES = [
        ("", ""),
        ("KASKO", "KASKO"),
        ("GALANG", "GALANG"),
        ("AZIGARANG", "AZIGARANG"),
        ("CENTRE", "CENTRE"),
        ("YADAWA", "YADAWA"),
        ("MBAKTAR", "MBAKTAR"),
    ]

    STATUT_PAIEMENT_CHOICES = [
        ("en_attente", "En attente"),
        ("paye", "Payé"),
        ("partiel", "Partiel"),
        ("impaye", "Impayé"),
    ]

    numero_facture = models.CharField(max_length=20, unique=True, blank=True, editable=False, verbose_name="N° Facture")
    matricule_client = models.CharField(max_length=30, blank=True, editable=False, verbose_name="Matricule Client")
    nom_client = models.CharField(max_length=100, verbose_name="Nom Client")
    quartier = models.CharField(max_length=100, choices=QUARTIER_CHOICES, default="KASKO", verbose_name="Quartier")
    numero_quartier = models.CharField(max_length=20, default="125")

    calibre = models.IntegerField(default=3)
    ancien_index = models.IntegerField()
    nouvel_index = models.IntegerField()
    conso = models.IntegerField(editable=False, default=0)

    mt_ht = models.IntegerField(editable=False, default=0, verbose_name="Montant Consommation")
    location_compteur = models.IntegerField(default=230)
    entretien_branchement = models.IntegerField(default=345)

    mois = models.CharField(max_length=30, default="SEPTEMBRE 2026")
    date_facture = models.DateField(default=datetime.date.today)
    net_a_payer = models.IntegerField(editable=False, default=0)
    statut_paiement = models.CharField(
        max_length=20,
        choices=STATUT_PAIEMENT_CHOICES,
        default="en_attente",
        verbose_name="Statut du paiement",
    )

    def save(self, *args, **kwargs):
        if not self.numero_facture:
            count = Facture.objects.count() + 1
            self.numero_facture = generate_invoice_number(datetime.date.today().year, count)

        self.conso = self.nouvel_index - self.ancien_index
        self.mt_ht = calculate_usage_amount(self.conso)
        self.net_a_payer = calculate_total_with_fees(
            self.mt_ht,
            self.location_compteur,
            self.entretien_branchement,
        )

        if not self.matricule_client:
            last = Facture.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.matricule_client = generate_client_matricule(datetime.date.today().year, next_id)

        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    nom = models.CharField(max_length=120, verbose_name="Nom")
    email = models.EmailField(max_length=200, verbose_name="Email")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    objet = models.CharField(max_length=200, verbose_name="Objet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    def __str__(self):
        return f"{self.nom} - {self.objet}"
