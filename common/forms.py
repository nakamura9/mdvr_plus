from django import forms
from common.models import Config
from crispy_forms.layout import Layout, Submit
from crispy_forms.helper import FormHelper

class ConfigForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Config
        widgets = {
            'email_password': forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email_address',
            'email_password',
            'smtp_server',
            'smtp_port',
            'default_reminder_email'
        )
        self.helper.add_input(Submit('submit', 'Submit'))