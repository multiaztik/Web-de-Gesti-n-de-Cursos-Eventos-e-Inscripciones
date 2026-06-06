from django import forms
from .models import Miembro, Curso

class MiembroForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = ['nombre', 'correo', 'cursos', 'foto', 'comprobante']
        help_texts = {
            'foto': 'La imagen no debe superar los 2 MB. Formatos permitidos: JPG, PNG, GIF, WebP.',
            'comprobante': 'El archivo no debe superar los 3 MB.',
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')

        if foto:
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no debe superar los 2 MB.')

            if hasattr(foto, 'content_type') and foto.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG, GIF o WebP.')

        return foto

    def clean_comprobante(self):
        comprobante = self.cleaned_data.get('comprobante')

        if comprobante and comprobante.size > 3 * 1024 * 1024:
            raise forms.ValidationError('El archivo no debe superar los 3 MB.')

        return comprobante

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion']