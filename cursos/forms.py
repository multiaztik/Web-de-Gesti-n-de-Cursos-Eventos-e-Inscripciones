from django import forms
from .models import Curso


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_termino',
                  'cupo_maximo', 'instructor', 'imagen', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre del curso debe tener al menos 3 caracteres.')
        return nombre

    def clean_cupo_maximo(self):
        cupo = self.cleaned_data.get('cupo_maximo')
        if cupo is not None and cupo <= 0:
            raise forms.ValidationError('El cupo máximo debe ser mayor que cero.')
        return cupo

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and hasattr(imagen, 'size'):
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede superar los 5 MB.')
            if hasattr(imagen, 'content_type') and imagen.content_type not in [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp'
            ]:
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG, GIF o WebP.')
        return imagen

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino')
        if fecha_inicio and fecha_termino:
            if fecha_termino < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de término no puede ser anterior a la fecha de inicio.'
                )
        return cleaned_data


class BusquedaCursoForm(forms.Form):
    q = forms.CharField(
        required=False, label='Buscar',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del curso...'})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Curso.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    instructor = forms.CharField(
        required=False, label='Instructor',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del instructor...'})
    )
