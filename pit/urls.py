from django.urls import path
from pit.views import Index, Report, Reset

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('report/', Report.as_view(), name='report'),
    path('reset/', Reset.as_view(), name='reset'),
]
