import os

from django import forms
from .models import Inscripcion


def _validar_archivo_evidencia(archivo):
    if archivo.size > 10 * 1024 * 1024:
        raise forms.ValidationError('El archivo no puede superar los 10 MB.')
    ext = os.path.splitext(archivo.name)[1].lower()
    extensiones_permitidas = ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx']
    if ext not in extensiones_permitidas:
        raise forms.ValidationError(
            f'Tipo de archivo no permitido. Use: {", ".join(extensiones_permitidas)}'
        )


class InscripcionForm(forms.ModelForm):
    """Formulario de gestión de inscripciones (administrador)."""
    class Meta:
        model = Inscripcion
        fields = ['alumno', 'curso', 'estado', 'evidencia']
        widgets = {
            'alumno': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'evidencia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_evidencia(self):
        archivo = self.cleaned_data.get('evidencia')
        if archivo and hasattr(archivo, 'size'):
            _validar_archivo_evidencia(archivo)
        return archivo

    def clean(self):
        cleaned_data = super().clean()
        alumno = cleaned_data.get('alumno')
        curso = cleaned_data.get('curso')
        if not alumno or not curso:
            return cleaned_data

        duplicado = Inscripcion.objects.filter(alumno=alumno, curso=curso)
        if self.instance.pk:
            duplicado = duplicado.exclude(pk=self.instance.pk)
        if duplicado.exists():
            raise forms.ValidationError('Este alumno ya está inscrito en este curso.')

        if not self.instance.pk:
            if curso.estado == 'cancelado':
                raise forms.ValidationError('Este curso está cancelado y no acepta inscripciones.')
            if curso.estado == 'cerrado':
                raise forms.ValidationError('Este curso está cerrado y no acepta inscripciones.')
            if not curso.tiene_cupo():
                raise forms.ValidationError('El curso ha alcanzado su cupo máximo.')

        return cleaned_data


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
            _validar_archivo_evidencia(archivo)
        return archivo
