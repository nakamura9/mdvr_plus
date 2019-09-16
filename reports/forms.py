from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Vehicle, Reminder

class HarshBrakingReportForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()
    vehicle = forms.ModelChoiceField(Vehicle.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('start',css_class='col-4'),
                Column('end',css_class='col-4'),
                Column('vehicle',css_class='col-4'),
            )
        )
        self.helper.add_input(Submit('submit', 'Generate'))

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'registration_number',
            'vehicle_type'
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = "__all__"
        widgets = {
            'reminder_message': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('vehicle', css_class="col-6"),
                Column('reminder_type', css_class="col-6")
            ),
            Row(
                Column('date', css_class="col-6"),
                Column('active', css_class="col-6")
            ),
            Row(
                Column('interval_days', css_class="col-6"),
                Column('interval_mileage', css_class="col-6")
            ),
            'reminder_email', 
            'reminder_message',
        )
        self.helper.add_input(Submit('submit', 'Submit'))