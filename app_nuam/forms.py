from django import forms
from .models import Calificacion
from datetime import datetime

class CalificacionForm(forms.ModelForm):
    
    # Campos adicionales para factores individuales (Factor 8 al 37)
    # Se generan dinámicamente
    
    class Meta:
        model = Calificacion
        fields = [
            'ejercicio', 'mercado', 'instrumento', 'descripcion',
            'fecha_pago', 'secuencia_evento', 'evento_capital',
            'valor_historico', 'dividendo', 'observaciones'
        ]
        widgets = {
            'ejercicio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ej., 2023',
                'min': '2000',
                'max': str(datetime.now().year + 1)
            }),
            'mercado': forms.Select(attrs={'class': 'form-control'}),
            # 'instrumento': forms.Select(attrs={'class': 'form-control'}),
            'instrumento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ej., JEEP'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese descripción'
            }),
            'fecha_pago': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'secuencia_evento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ej., SEQ001'
            }),
            'evento_capital': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Evento de capital (opcional)'
            }),
            'valor_historico': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'dividendo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Opciones para mercado e instrumento
        self.fields['mercado'].widget = forms.Select(
            choices=[
                ('', 'Seleccione un mercado'),
                ('AC', 'Acciones Cerradas'),
                ('AA', 'Acciones Abiertas'),
            ],
            attrs={'class': 'form-control'}
        )
        
        for i in range(8, 38):
            field_name = f'factor_{i}'
            self.fields[field_name] = forms.DecimalField(
                required=False,
                max_digits=12,
                decimal_places=8,
                initial=0.00,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control form-control-sm',
                    'step': '0.00000001',
                    'placeholder': '0.00'
                }),
                label=f'Factor {i:02d}'
            )
            
            # Si estamos editando, prellenar con valores existentes
            if self.instance and self.instance.pk and self.instance.factores:
                self.fields[field_name].initial = self.instance.factores.get(field_name, 0)
    
    def clean_ejercicio(self):
        ejercicio = self.cleaned_data.get('ejercicio')
        if ejercicio and (ejercicio < 2000 or ejercicio > datetime.now().year + 1):
            raise forms.ValidationError('El ejercicio debe estar entre 2000 y el año actual + 1')
        return ejercicio
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Consolidar factores en un diccionario
        factores = {}
        for i in range(8, 38):
            field_name = f'factor_{i}'
            valor = cleaned_data.get(field_name, 0)
            if valor is not None:
                factores[field_name] = float(valor)
        
        cleaned_data['factores'] = factores
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Guardar factores desde cleaned_data
        if 'factores' in self.cleaned_data:
            instance.factores = self.cleaned_data['factores']
        
        if commit:
            instance.save()
        
        return instance


class FiltroCalificacionesForm(forms.Form):
    mercado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + [
            ('AC', 'Acciones Cerradas'),
            ('AA', 'Acciones Abiertas'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    origen = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Calificacion.ORIGENES),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    ejercicio = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Año'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Calificacion.ESTADOS),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )