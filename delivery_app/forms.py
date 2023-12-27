from django import forms

class DeliveryOrderForm(forms.Form):
    customer_name = forms.CharField(max_length=255)
    contact_number = forms.CharField(max_length=15)
    delivery_address = forms.CharField(widget=forms.Textarea)
    items = forms.CharField(widget=forms.Textarea)
    pickup_location = forms.CharField(max_length=255)
    pickup_contact = forms.CharField(max_length=15)
    delivery_date = forms.DateField()
