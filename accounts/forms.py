from django.contrib.auth.forms import UserCreationForm

from .models import Member


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Member
        fields = ('username', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['phone'].required = True
