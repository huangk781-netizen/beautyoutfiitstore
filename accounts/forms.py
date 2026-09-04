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


class JapaneseRegisterForm(RegisterForm):
    class Meta(RegisterForm.Meta):
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'phone': '電話番号',
        }
        help_texts = {
            'username': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
