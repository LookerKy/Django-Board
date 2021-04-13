from django.test import TestCase
from ..forms import SignUpForm


class SignUpFormTest(TestCase):
    def test_form_has_field(self):
        form = SignUpForm()
        expected = ['email', 'username', 'password1', 'password2']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
