from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, 
                                 Submit, 
                                 Row, 
                                 Column,
                                 HTML)
from reports import models
from django_select2.forms import Select2Widget, Select2MultipleWidget
class HarshBrakingReportForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()
    vehicle = forms.ModelChoiceField(models.Vehicle.objects.all(),
        widget=Select2Widget)

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
        model = models.Vehicle
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'registration_number',
            'vehicle_type',
            Row(
                Column('make', css_class='col-4'),
                Column('model', css_class='col-4'),
                Column('year', css_class='col-4'),
            ),
            Row(
                Column('seats', css_class='col-6'),
                Column('loading_capacity_tons', css_class='col-6'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ReminderForm(forms.ModelForm):
    class Meta:
        model = models.Reminder
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

class NoteForm(forms.ModelForm):
    class Meta:
        exclude = "date",
        model = models.Note
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('author', css_class="col-6"),
                Column('subject', css_class="col-6")
            ),
            'note',
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class DriverForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Driver
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
            'vehicles': Select2MultipleWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('last_name', css_class="col-6"),
                Column('first_names', css_class="col-6")
            ),
            Row(
                Column('date_of_birth', css_class="col-6"),
                Column('gender', css_class="col-6")
            ),
            Row(
                Column('license_number', 
                        'license_issuing_date', 
                        'license_class', css_class="col-6"),
                Column('phone_number','address', css_class="col-6")
            ),
            'photo',
            'vehicles'

        )
        self.helper.add_input(Submit('submit', 'Submit'))

class InsuranceForm(forms.ModelForm):
    reminder_days = forms.CharField(widget=forms.NumberInput)
    class Meta:
        exclude = 'notes',
        model = models.Insurance
        widgets = {
            'vehicle': forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'vendor',
            Row(
                Column('coverage', css_class="col-6"),
                Column('valid_until', css_class="col-6")
            ),
            'vehicle',
            'reminder_days'
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class FitnessCertificateForm(forms.ModelForm):
    reminder_days = forms.CharField(widget=forms.NumberInput)
    class Meta:
        exclude = 'notes',
        model = models.VehicleCertificateOfFitness
        widgets = {
            'vehicle': forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'location',
            Row(
                Column('date', css_class="col-6"),
                Column('valid_until', css_class="col-6")
            ),
            'vehicle',
            'reminder_days'
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ServiceLogForm(forms.ModelForm):
    class Meta:
        model = models.VehicleServiceLog
        fields = '__all__'
        widgets = {
            'vehicle': forms.HiddenInput,
            'service': Select2Widget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'vendor',
            Row(
                Column('date', css_class="col-6"),
                Column('odometer', css_class="col-6")
            ),
            'service',
            'vehicle'
        )
        self.helper.add_input(Submit('submit', 'Submit'))



class ServiceForm(forms.ModelForm):
    class Meta:
        model = models.VehicleService
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            'repeat_method',
            Row(
                Column('frequency_time', css_class="col-6"),
                Column('interval_mileage', css_class="col-6")
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class IncidentForm(forms.ModelForm):
    class Meta:
        model = models.Incident
        fields = '__all__'
        widgets = {
            'vehicle': forms.HiddenInput,
            'driver': Select2Widget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'driver',
            'vehicle',
            'description',
            Row(
                Column('date', css_class="col-6"),
                Column('location', css_class="col-6")
            ),
            Row(
                Column('number_of_vehicles_involved', css_class="col-6"),
                Column('number_of_pedestrians_involved', css_class="col-6")
            ),
            'report'
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class MedicalForm(forms.ModelForm):
    reminder_days = forms.CharField(widget=forms.NumberInput)

    class Meta:
        model = models.DriverMedical
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'driver',
            'location',
            Row(
                Column('date', css_class="col-6"),
                Column('valid_until', css_class="col-6")
            ),
            'reminder_days'
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class DDCFrom(forms.ModelForm):
    reminder_days = forms.CharField(widget=forms.NumberInput)

    class Meta:
        model = models.DDC
        fields = '__all__'
        widgets = {
            'driver': forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'number',
            'expiry_date',
            'reminder_days',
            'driver'
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ReminderCategoryForm(forms.ModelForm):
    class Meta:
        model = models.ReminderCategory
        fields ="__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description'
        )
        self.helper.add_input(Submit('submit', 'Submit'))