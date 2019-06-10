from django import forms


def validate_file_extension(value):
    # print value.name
    # print value.name.endswith('.csv')
    if not value.name.endswith('.csv'):
        # print 'Wrong file'

        # this wont upload other files except csv, but won't show any error to user as well
        raise forms.ValidationError('Only CSV')

class StartProjectComparatorForm(forms.Form):
    url_file  = forms.FileField(validators=[validate_file_extension])
    xpath_file = forms.FileField(validators=[validate_file_extension])    
    platform_import_file = forms.FileField(validators=[validate_file_extension])

    RUN_CHOICE = (
	    ('1', 'Hight Priority. Gives report when max error reached.'),
	    ('2', 'Gives bulk report where all comparison completed.'),
	)
    run_priority = forms.ChoiceField(
    	choices = RUN_CHOICE,
        required = True,
    )


class PasswordUpdateForm(forms.Form):
    current_password  = forms.CharField(label='Current Password',widget=forms.PasswordInput)
    new_password = forms.CharField(label='New Password',widget=forms.PasswordInput)    


