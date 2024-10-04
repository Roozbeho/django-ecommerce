from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Title'}
        )
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Description'}
        )