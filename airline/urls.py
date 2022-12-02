from django.urls import path
from airline.views import DeltaScheduleEntry, Oauth2CallbackView, CalAuthView, workdeltschedulegoogle, setcalid,importingevents,DeletemultipleQuery, SimpleUpload
urlpatterns = [
    path('google', workdeltschedulegoogle, name="googleschedule"),
    path('import', importingevents, name="importingevents"),
    path('setcalid/<str:id>', setcalid, name="setcalid"),
    path('calauth/', CalAuthView, name='cal_auth'),
    path('oauth2callback/', Oauth2CallbackView.as_view(), name='oauth2callback'),
    path('upload', SimpleUpload.as_view(),name="upload"),
    path('', DeltaScheduleEntry.as_view(), name="deltaschedule"),
    path('deletelist/', DeletemultipleQuery.as_view(), name = "deletequery"),
    path('delete/', DeletemultipleQuery.as_view(), name = "deletemultiple"),
]