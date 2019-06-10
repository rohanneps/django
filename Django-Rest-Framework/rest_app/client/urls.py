from django.urls import path
from .views import (
		ClientDistinctList
		
	)
from rest_framework.urlpatterns import format_suffix_patterns


# project namespace
app_name='client'


urlpatterns = [
    path('all/', ClientDistinctList.as_view(), name='clientlist'),

]

# for handling for cases like /project/1.json
urlpatterns = format_suffix_patterns(urlpatterns)