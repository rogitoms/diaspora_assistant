from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),                                        # frontend page
    path("api/submit/", views.submit_request, name="submit"),                   # submit new request
    path("api/tasks/", views.get_tasks, name="get_tasks"),                      # get all tasks
    path("api/tasks/<str:task_code>/status/", views.update_status, name="update_status"),  # update status
]