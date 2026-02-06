from django.urls import path, re_path
from .views import IvsSettingsView, IvsCheckinView, IvsPlayerView

app_name = 'pretix_ivs_plugin'

urlpatterns = [
    path('control/event/<str:organizer>/<str:event>/settings/ivs/', 
         IvsSettingsView.as_view(), name='settings'),
]

event_patterns = [
    re_path(r'^order/(?P<order>[^/]+)/(?P<secret>[A-Za-z0-9]+)/ivs_checkin/$', 
            IvsCheckinView.as_view(), name='checkin'),
    path('ivs-iframe/', IvsPlayerView.as_view(), name='ivs-iframe'),
]
