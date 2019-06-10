from rest_framework import serializers
from project.models import Project
from django.conf import settings

def validate_id(value):
	if value is None:
		raise serializers.ValidationError('This field is required')
	if type(value)!=int:
		raise serializers.ValidationError('This field should be interger')

class ProjectInputSerializer(serializers.ModelSerializer):
	class Meta:
		model = Project
		fields = ('client_name', 'file_name')


class ProjectDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Project
		fields = ('id', 'client_name', 'start_date', 'file_name', 'status', 'failed_log','total_records','total_unique_products')


class ProjectStartSerializer(serializers.Serializer):
	id = serializers.IntegerField(validators=[validate_id])


class ProjectInitSerializer(serializers.Serializer):
	client_name = serializers.CharField(allow_blank=False, max_length=300)
	file_name = serializers.CharField(allow_blank=False, max_length=300)

class FindProjectByClientSerializer(serializers.Serializer):
	client_name = serializers.CharField(allow_blank=False, max_length=300)
	all = serializers.CharField(required=False,allow_blank=True, max_length=300)			# Cases where pagination is to be skipped, field is required, value is arbitary.

class FindProjectByDateSerializer(serializers.Serializer):
	from_date = serializers.CharField(allow_blank=False, max_length=300)
	to_date = serializers.CharField(allow_blank=False, max_length=300)

class FindProjectByStatusSerializer(serializers.Serializer):
	status = serializers.ChoiceField(choices=settings.PROJECT_STATUS_LIST)

class UpdateProjectHumanProcessStatusSerializer(serializers.Serializer):
	id = serializers.IntegerField(validators=[validate_id])
	status = serializers.ChoiceField(choices=settings.PROJECT_STATUS_LIST)

class FindProjectByClientDateStatusSerializer(serializers.Serializer):
	client_name = serializers.CharField(required=False,allow_blank=True, max_length=300)
	from_date = serializers.CharField(required=False,allow_blank=True, max_length=300)
	to_date = serializers.CharField(required=False,allow_blank=True, max_length=300)
	status_list = (
		('Pending', 'Pending'),
		('InProgress', 'InProgress'),
		('Completed', 'Completed'),
		('Failed', 'Failed'),
		('Terminated','Terminated'),
		('H_InProgress', 'H_InProgress'),
        ('H_Completed', 'H_Completed'),
		('All','All')					# This status is not present in model, but is used to retrieve all projects with any status
	)
	status = serializers.ChoiceField(choices=status_list, allow_blank=True, default='All')