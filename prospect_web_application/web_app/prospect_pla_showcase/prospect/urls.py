from django.urls import path

from .views import home, ProspectListView, ProspectDetailView, schedule_prospect, GoogleDetailsListView, AmazonDetailsListView

app_name = 'prospect'

urlpatterns = [
    path('', home, name='index'),
    path('all', ProspectListView.as_view(), name='all_prospects'),
    path('run_details/google', GoogleDetailsListView.as_view(), name='google_run_details'),
    path('run_details/amazon', AmazonDetailsListView.as_view(), name='amazon_run_details'),
    path('<int:pk>/', ProspectDetailView.as_view(), name='prospect_detail'),
    path('schedule', schedule_prospect, name='schedule_prospect')
]