from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^listing$', views.list_items),
    url(r'^register$', views.create_user),
    url(r'^logout$', views.logout),
    url(r'^wish_items/add$', views.create_item),
    url(r'^wish_items/(?P<wish_id>\d+)$', views.show),
    url(r'^wish_items/remove_wish/(?P<wish_id>\d+)$', views.remove_wish),
    url(r'^wish_items/delete_wish/(?P<wish_id>\d+)$', views.delete_wish),
    url(r'^wish_items/add_to_list/(?P<wish_id>\d+)$', views.add_to_list)
]

