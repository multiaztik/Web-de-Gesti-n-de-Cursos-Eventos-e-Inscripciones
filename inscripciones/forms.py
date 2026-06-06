from django import forms
from .models import Inscripcion


class EvidenciaForm(forms.ModelForm):
    """Formulario para subir evidencia de una inscripción."""
    class Meta:
        model = Inscripcion
        fields = ['evidencia']
        widgets = {
            'evidencia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_evidencia(self):
        archivo = self.cleaned_data.get('evidencia')
        if archivo and hasattr(archivo, 'size'):
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar los 10 MB.')
            extensiones_permitidas = ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx']
            import os
            ext = os.path.splitext(archivo.name)[1].lower()
            if ext not in extensiones_permitidas:
                raise forms.ValidationError(
                    f'Tipo de archivo no permitido. Use: {", ".join(extensiones_permitidas)}'
                )
        return archivo
