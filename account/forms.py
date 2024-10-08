from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm


from .models import Address, Customer


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(max_length=255, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=255, widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ["email", "username"]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "Email"})
        self.fields["username"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "Username"})
        self.fields["password1"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "Repeat password"})

    def clean_password2(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("Password must be match"))

        self._clean_password(password2)
        return password2

    def _clean_password(self, password):
        if len(password) < 6:
            raise forms.ValidationError(_("password length must have at least 6 characters"))
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError(_("password must have at laest one number"))
        if not any(char.isupper() for char in password):
            raise forms.ValidationError(_("password must have upper case characters"))
        if not any(char.islower() for char in password):
            raise forms.ValidationError(_("password must have lower case characters"))
        return password

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.CharField(max_length=255, widget=forms.EmailInput)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control mb-3", "Placeholder": "Email"})
        self.fields["password"].widget.attrs.update({"class": "form-control mb-3", "placeholder": "Password"})


class AccountVerificationForm(forms.Form):
    code = forms.IntegerField(max_value=999999, min_value=100000)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["customer", "is_default"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "first_name"})
        self.fields["last_name"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "last_name"})
        self.fields["phone_number"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "phone_number"})
        self.fields["postal_code"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "postal_code"})
        self.fields["state"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "state"})
        self.fields["city"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "city"})
        self.fields["address_line_1"].widget.attrs.update(
            {"class": "form-control mb-4", "placeholder": "address_line_1"}
        )
        self.fields["address_line_2"].widget.attrs.update(
            {"class": "form-control mb-4", "placeholder": "address_line_2"}
        )


class ChangeCustomerInformationForm(forms.ModelForm):
    password=None
    class Meta:
        model = Customer
        fields = ['email', 'username']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder':'Email address', 'readonly':'readonly'}
        )
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'User name'}
        )

    def clean(self):
        if Customer.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(_('thise uesrname is already exists'))
        return self.cleaned_data
    
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        # self.user = user
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "Old Password"})
        self.fields["new_password1"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "New Password"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control mb-4", "placeholder": "Repeat New Password"})