from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^meal/new/$', views.meal_new, name="meal_new"),
    url(r'^meal/(?P<meal_id>\d+)/$', views.meal_detail, name="meal_detail"),
    url(r'^meal/(?P<meal_id>\d+)/dish/new/$', views.add_dish, name="add_dish"),
    url(r'^dish/(?P<dish_id>\d+)/$', views.dish_detail, name="dish_detail"),
    url(r'^types/$', views.types, name="types"),
    url(r'^types/(?P<res_name>\w+)/$', views.types_detail, name="types_detail"),
    url(r'^inventory/$', views.invent, name="inventory",
            kwargs={'showAll': False}),
    url(r'^inventory/all/$', views.invent, name="inventory_all",
            kwargs={'showAll': True}),
    url(r'^inventory/(?P<inst_id>\d+)/$',
        views.invent_detail, name="inv_detail"),
    url(r'^inventory/new/$', views.invent_new_item, name="inv_new"),
]
