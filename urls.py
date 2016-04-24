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

    url (   r'^meal/(?P<pk>\d+)/del/$',
            views.DeleteMeal.as_view(),
            name="meal_delete",
        ),

    url (   r'^meal/(?P<meal_id>\d+)/dish/new/$',
            views.NewDish.as_view(),
            name="add_dish"
        ),

    url (   r'^dish/(?P<pk>\d+)/del/$',
            views.DeleteDish.as_view(),
            name="dish_delete"
        ),

    url (   r'^dish/(?P<pk>\d+)/$',
            views.DishView.as_view(),
            name="dish_detail"
        ),

    url (   r'^types/$',
            views.TypesOverview.as_view(),
            name="types"
        ),

    url (   r'^types/(?P<slug>\w+)/$',
            views.TypesView.as_view(),
            name="types_detail"
        ),

    url (   r'^instances/$',
            views.StdInstListView.as_view(),
            name="std_insts"
        ),

    url (   r'^instances/(?P<pk>\d+)/$',
            views.StdInstDetailView.as_view(),
            name="std_inst_detail"
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

    url (   r'^standard_instance/$',
            views.getStandardInst,
            name="std_inst_raw"
        ),

    url (   r'^ticket/(?P<pk>\d+)/del/$',
            views.DeleteTicket.as_view(),
            name="inv_delete_ticket",
        ),

    url (   r'^inventory/new/$',
            views.NewInst.as_view(),
            name="inv_new"
        ),

    url (   r'^inventory/new_std/$',
            views.NewInstStd.as_view(),
            name="inv_new_std"
        ),

    url (   r'^about/$',
            TemplateView.as_view(template_name="mealy/about.html"),
            name="about"
        ),
]
