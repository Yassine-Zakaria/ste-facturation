import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ste_facturation.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
agent_group, _ = Group.objects.get_or_create(name='Agents de collecte')

clients = [
    ('client_001', 'Client@123', 'Ali', 'Benali'),
    ('client_002', 'Client@123', 'Sara', 'Khaled'),
    ('client_003', 'Client@123', 'Yacine', 'Ait'),
]

agents = [
    ('agent_amine', 'Agent@123', 'Amine', 'Collecte'),
    ('agent_fatima', 'Agent@123', 'Fatima', 'Collecte'),
    ('agent_brahim', 'Agent@123', 'Brahim', 'Collecte'),
]

created_users = []

for username, password, first_name, last_name in clients:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name},
    )
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    user.is_staff = False
    user.save()
    created_users.append({'type': 'client', 'username': username, 'created': created, 'password': password})

for username, password, first_name, last_name in agents:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name},
    )
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    user.is_staff = False
    user.groups.add(agent_group)
    user.save()
    created_users.append({'type': 'agent', 'username': username, 'created': created, 'password': password})

print('Comptes créés :')
for item in created_users:
    print(f"- {item['type']}: {item['username']} / {item['password']}")
