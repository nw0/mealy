from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url (   r'^$',
            views.index,
            name="index"
        ),

    url (   r'^meal/new/$',
            views.NewMeal.as_view(),
            name="meal_new"
        ),

    url (   r'^meal/(?P<pk>\d+)/$',
            views.MealView.as_view(),
            name="meal_detail"
        ),

    url (   r'^meal/(?P<meal_id>\d+)/dish/new/$',
            views.NewDish.as_view(),
            name="add_dish"
        ),

    url (   r'^dish/(?P<pk>\d+)/$',
            views.DishView.as_view(),
            name="dish_detail"
        ),

    url (   r'^types/$',
            views.TypesView.as_view(),
            name="types"
        ),

    url (   r'^types/(?P<slug>\w+)/$',
            views.TypesDetailView.as_view(),
            name="types_detail"
        ),

    url (   r'^inventory/$',
            views.InventView.as_view(),
            name="inventory",
            kwargs={'showAll': False}
        ),

    url (   r'^inventory/all/$',
            views.InventView.as_view(),
            name="inventory_all",
            kwargs={'showAll': True}
        ),

    url(    r'^inventory/(?P<inst_id>\d+)/$',
            views.invent_detail,
            name="inv_detail"
        ),

    url (   r'^ticket/(?P<pk>\d+)/del/$',
            views.DeleteTicket.as_view(),
            name="inv_delete_ticket",
        ),

    url (   r'^inventory/new/$',
            views.NewInst.as_view(),
            name="inv_new"
        ),

    url (   r'^about/$',
            TemplateView.as_view(template_name="mealy/about.html"),
            name="about"
        ),
]
