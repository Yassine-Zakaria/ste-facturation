from django import forms

from .models import ContactMessage, Facture


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'telephone', 'objet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+235 ...'}),
            'objet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet de votre message'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Décrivez votre demande...'}),
        }


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = '__all__'
        labels = {
            'numero_facture': 'N° Facture',
            'matricule_client': 'Matricule Client',
            'nom_client': 'Nom Client',
            'quartier': 'Quartier',
            'numero_quartier': 'N° Quartier',
            'calibre': 'Calibre',
            'ancien_index': 'Ancien Index',
            'nouvel_index': 'Nouvel Index',
            'location_compteur': 'Location Compteur',
            'entretien_branchement': 'Entretien Branchement',
            'mois': 'Mois',
            'date_facture': 'Date Facture',
            'statut_paiement': 'Statut du paiement',
        }
        widgets = {
            'statut_paiement': forms.Select(attrs={'class': 'form-control'}),
        }
