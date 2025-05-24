# analysis/forms.py
from django import forms
from .models import EEGData

class EEGUploadForm(forms.ModelForm):
    class Meta:
        model = EEGData
        fields = ['original_file', 'sampling_rate']
        labels = {
            'original_file': 'Arquivo EEG (CSV)',
            'sampling_rate': 'Taxa de Amostragem (Hz)'
        }