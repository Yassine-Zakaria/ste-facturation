# STE Facturation

Application de gestion de factures d’eau avec tableau de bord, historique et impression.

## Structure du projet

```text
STE_facturation/
├── manage.py
├── README.md
├── db.sqlite3
├── factures/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_services.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   ├── templates/
│   │   └── factures/
│   └── static/
│       └── factures/
├── ste_facturation/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── factures_core/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    └── models.py
```

## Bonnes pratiques appliquées

- Séparation des formulaires dans `forms.py`
- Séparation de la logique métier dans `services.py`
- Ajout de tests pour les règles métier
- Mise à jour des vues pour utiliser des composants plus propres
- Préparation de la structure pour un projet plus professionnel

## Prochaines étapes recommandées

1. Séparer les settings par environnement (`base.py`, `dev.py`, `prod.py`)
2. Ajouter des tests sur les vues et les modèles
3. Créer un thème centralisé et un layout `base.html`
4. Ajouter un système robust de gestion d’environnement (`.env`)
