from django import forms
from common.models import Config
from crispy_forms.layout import Layout, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Tab, TabHolder


class ConfigForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Config
        labels = {
            'harsh_braking_delta': 'Harsh Braking Threshold(change in speed in km/hr per 3s)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Email',
                    'email_address',
                    'email_password',
                    'smtp_server',
                    'smtp_port',
                    'default_reminder_email',
                    
                ),
                Tab('Server',
                    'server_ip',
                    'server_domain',
                    'server_port',
                    'conn_account',
                    'conn_password',
                ),
                Tab('Report Config',
                'DDC_reminder_days',
                'company_name',
                'speeding_threshold',
                'harsh_braking_delta',
                'daily_report_generation_time'
                )
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))