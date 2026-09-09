from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class JapaneseRegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse('jp_register')

    def valid_payload(self, **overrides):
        payload = {
            'username': '日本テスト会員',
            'email': 'jp-customer@example.jp',
            'phone': '090-1234-5678',
            'password1': 'Secure-JP-2026!',
            'password2': 'Secure-JP-2026!',
            'next': reverse('japan_landing'),
        }
        payload.update(overrides)
        return payload

    def test_validation_errors_are_rendered_in_japanese(self):
        response = self.client.post(
            self.url,
            self.valid_payload(email='', phone='', password2='Different-JP-2026!'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'このフィールドは必須です。', count=2)
        self.assertContains(response, '確認用パスワードが一致しません。')
        self.assertNotContains(response, 'この欄位は必須です。')
        self.assertFalse(get_user_model().objects.exists())

    def test_valid_registration_creates_member_and_logs_in(self):
        response = self.client.post(self.url, self.valid_payload())

        self.assertRedirects(response, reverse('japan_landing'))
        member = get_user_model().objects.get(username='日本テスト会員')
        self.assertEqual(member.email, 'jp-customer@example.jp')
        self.assertEqual(member.phone, '090-1234-5678')
        self.assertTrue(member.check_password('Secure-JP-2026!'))
        self.assertEqual(int(self.client.session['_auth_user_id']), member.pk)
