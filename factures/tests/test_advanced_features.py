from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from factures.models import Facture, ContactMessage


class AdvancedPresentationFeaturesTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin2', password='secret123', is_staff=True
        )

    def test_contact_form_submits_and_saves_message(self):
        response = self.client.post(
            reverse('contact'),
            {
                'nom': 'Moussa Ali',
                'email': 'moussa@example.com',
                'telephone': '+22890000000',
                'objet': 'Demande de facture',
                'message': 'Je souhaite obtenir mon relevé d’eau.',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().objet, 'Demande de facture')
        self.assertEqual(len(mail.outbox), 1)

    def test_payment_page_uses_real_status_values(self):
        self.client.force_login(self.admin)
        Facture.objects.create(
            nom_client='Amina Yao',
            quartier='KASKO',
            numero_quartier='15',
            ancien_index=100,
            nouvel_index=130,
            statut_paiement='paye',
        )

        response = self.client.get(reverse('paiements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payé')

    def test_export_report_returns_pdf(self):
        self.client.force_login(self.admin)
        Facture.objects.create(
            nom_client='Élodie d’Angor',
            quartier='CENTRE',
            numero_quartier='8',
            ancien_index=50,
            nouvel_index=75,
            statut_paiement='paye',
        )

        response = self.client.get(reverse('export_report_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
