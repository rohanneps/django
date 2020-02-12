from django import forms
from .models import Prospect
# import pandas as pd
from helpers import helper
from django.conf import settings


class ProspectForm(forms.ModelForm):

	platform = forms.ChoiceField(choices=settings.PLATFORM_LIST, required=True)

	class Meta:
		model = Prospect
		fields = ['name','file_name','email_recipients','platform']
		
	def __init__(self, *args, **kwargs):
		super(ProspectForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs.update({'data-toggle' :'tooltip', 'data-placement':'right','title':'Name of Prospect'})
		self.fields['name'].label = "Prospect Name"
		self.fields['file_name'].widget.attrs.update({'data-toggle' :'tooltip', 'data-placement':'right','title':'Shoud be tsv file. Should Contain "Search Keyword" column.'})
		self.fields['file_name'].label = "Keyword File"
		self.fields['platform'].label = "Platform"
		self.fields['platform'].widget.attrs.update({'data-toggle' :'tooltip', 'data-placement':'right','title':'Platform to Scrape'})
		self.fields['email_recipients'].widget.attrs.update({'data-toggle' :'tooltip', 'data-placement':'right','title':'Comma-separated email list.'})
		self.fields['email_recipients'].label = "List of Email Recipients"

	def clean_file_name(self):
		file_name = self.cleaned_data['file_name']
		file_ext = file_name.name.split('.')[-1].lower()
		
		if file_ext not in ['tsv']:
			raise forms.ValidationError("Input file needs to be tsv.")

		# prospect_df = pd.read_csv(file_name, sep='\t')

		prospect_df_column_list = helper.get_column_header_list(file_name)

		missing_headers = list(set(settings.MANDATORY_COLUMN_HEADERS)-set(prospect_df_column_list))

		
		if len(missing_headers)>0:
			raise forms.ValidationError('Fields(s) \'{}\' not in the file columns.'.format('\', \''.join(missing_headers)))

		# add validation for file headers
		return file_name