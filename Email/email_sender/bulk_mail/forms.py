from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField()

class ColumnMappingForm(forms.Form):
    name_column = forms.CharField(required=False)
    email_column = forms.CharField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
