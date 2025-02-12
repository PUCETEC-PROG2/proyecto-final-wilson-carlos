from django import forms
from .models import Clientes

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = [
            'nombre', 'apellido', 'correo_electronico', 'telefono',
            'direccion', 'ciudad', 'provincia', 'pais', 'fecha_registro'
        ]
        widgets = {
            'fecha_registro': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
