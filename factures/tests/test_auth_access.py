from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthAccessTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.client_user = self.user_model.objects.create_user(
            username='client', password='secret123'
        )
        self.admin_user = self.user_model.objects.create_user(
            username='admin', password='secret123', is_staff=True
        )

    def test_client_login_redirects_to_client_space(self):
        response = self.client.post(
            reverse('client_login'),
            {'username': 'client', 'password': 'secret123'},
            follow=True,
        )
        self.assertRedirects(response, reverse('client_space'))

    def test_admin_pages_require_staff(self):
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('liste_factures'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_agent_login_redirects_to_agent_space(self):
        from django.contrib.auth.models import Group

        agent_group = Group.objects.create(name='Agents de collecte')
        agent_user = self.user_model.objects.create_user(
            username='agent', password='secret123'
        )
        agent_user.groups.add(agent_group)

        response = self.client.post(
            reverse('agent_login'),
            {'username': 'agent', 'password': 'secret123'},
            follow=True,
        )
        self.assertRedirects(response, reverse('agent_space'))
