from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from helpers.endpoint_info import ENDPOINT_DICT




@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def endpoint_info(request, format=None):
	
	if request.method == 'POST':
		request_data_headers = request.data.keys()

		if 'endpoint' in request_data_headers:
			endpoint = request.data['endpoint']
			endpoint_list = ENDPOINT_DICT.keys()
			if endpoint in endpoint_list:
				return Response({'response':ENDPOINT_DICT[endpoint]})
			else:
				return Response({'response':'Provide an endpoint listed: '+','.join(endpoint_list) })
		else:
			return Response({'response':'Fields "endpoint" is required.'})


@api_view(['GET'])
def api_root(request, format=None):
	return Response({
		'endpointinfo': reverse('endpoint_info', request=request, format=format),

		# project app
		'createproject': reverse('project:createproject', request=request, format=format),
		'project': reverse('project:projectdetail', kwargs={'pk':1}, request=request, format=format),
		'projects': reverse('project:projectlist', request=request, format=format),
		'projectids': reverse('project:projectidlist', request=request, format=format),
		'startproject': reverse('project:startproject', request=request, format=format),
		'getinprogressproject': reverse('project:getinprogressproject', request=request, format=format),
		'terminateinprogressproject': reverse('project:terminateinprogressproject', request=request, format=format),
		'getprojectmatchnotmatchcount': reverse('project:getprojectmatchnotmatchcount', kwargs={'project_id':1}, request=request, format=format),
		'updatehumanverification': reverse('project:updatehumanverification', request=request, format=format),
		#search app
		'searchprojectsbyclient': reverse('search:searchprojectsbyclient', request=request, format=format),
		'searchprojectsbydate': reverse('search:searchprojectsbydate', request=request, format=format),
		'searchprojectsbystatus': reverse('search:searchprojectsbystatus', request=request, format=format),
		'searchprojectsbyclientdatestatus': reverse('search:searchprojectsbyclientdatestatus', request=request, format=format),
		'searchprojectdetailedreport': reverse('search:searchprojectdetailedreport', request=request, format=format),
		'initiatematchdownload': reverse('download:initiatematchdownload', kwargs={'project_id':1}, request=request, format=format),
		
		#client app	
		'clients': reverse('client:clientlist', request=request, format=format),
	})