from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from .forms import MealForm, DishForm, TicketForm, TicketFormSet, \
                    InstAttribForm, NewInstForm, NewInstStdForm
import json, datetime, time

from .models import Resource_Type, Resource_Inst, Resource_Ticket, \
                TicketManager, Meal, Dish, Standard_Inst
from .admin import other_checks
# Create your views here.

decs = [ login_required, user_passes_test(other_checks)]

SEMI_OPEN_STATE_THRESHOLD = 10
ENABLE_CAL_PROGRESS_BARS = True

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    fifth_jan = datetime.date(iso_year, 1, 5)
    _, fifth_jan_week, fifth_jan_day = fifth_jan.isocalendar()
    return fifth_jan + datetime.timedelta(days=iso_day-fifth_jan_day,
                                            weeks=iso_week-fifth_jan_week)

@login_required
@user_passes_test(other_checks)
def index(request):
    #   We want to know what meals there are
    meal_list = Meal.objects.filter(
                        meal_owner=request.user.id).order_by('-cons_time')
    cal = {}
    for meal in meal_list:
        iy, im, iw = meal.cons_time.isocalendar()
        if (iy, im) not in cal:
            cal[(iy, im)] = {}
        if iw not in cal[(iy, im)]:
            cal[(iy, im)][iw] = []
        cal[(iy, im)][iw].append(meal)

    for e in cal:
        #   e is a week, e.g. (2016, 1)
        #   cal[e] is a dict of meals by day {iw: [meal]} that week
        weekMeals = [[] for i in range(7)]
        tot, mc, opensum = 0, 0, 0
        for w in xrange(7):
            weekMeals[w] = cal[e][w+1] if w+1 in cal[e] else []
            for meal in weekMeals[w]:
                tot += meal.get_meal_cost()
                mc += 1
                opensum += meal.open_cost
            weekMeals[w] = [ (u"%s \xA3%.2f" % (meal.meal_type[0],
                                meal.get_meal_cost()/100),
                                reverse("mealy:meal_detail", args=(meal.id,)),
                                meal.open_cost, meal.get_meal_cost())
                                for meal in weekMeals[w]]
            # weekMeals[0] = (monday) [ ("L 2.77", det_link, 0.56, 2.77), ... ]
            weekMeals[w] = [iso_to_gregorian(e[0], e[1], w+1).strftime("%b %d"),
                                weekMeals[w]]
            # weekMeals[0] = [ "Mar 14", [("L...", det_link, 0.56, 2.77), ...] ]
            weekMeals[w][1].sort()
        weekMeals.append(["", [(u"T \xA3%.2f (%.2f)" % (tot/100, opensum/100),
                                    False, opensum, tot),
                            (u"A \xA3%.2f (%.2f)" %
                                    (tot/100/mc, opensum/100/mc), False, opensum/mc, tot/mc)]])
        cal[e] = weekMeals
    cal = sorted(list(cal.items()), reverse=True)

    template    = loader.get_template("mealy/meals.html")
    contDict =  {   'meal_list': meal_list,
                    'mtypes': Meal.MEAL_TYPES,
                    'meal_form': MealForm,
                    'user':     request.user,
                    'cal_meals': cal,
                    'semi_open': SEMI_OPEN_STATE_THRESHOLD,
                    'prog_bars': ENABLE_CAL_PROGRESS_BARS,
                }
    return HttpResponse(template.render(contDict, request))

@method_decorator(decs, name='dispatch')
class MealView(generic.DetailView):
    def get_queryset(self):
        return Meal.objects.filter( id=self.kwargs['pk'],
                                    meal_owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MealView, self).get_context_data(**kwargs)
        context['dish_form']    = DishForm
        return context

@method_decorator(decs, name='dispatch')
class NewMeal(generic.edit.CreateView):
    form_class  = MealForm
    success_url = reverse_lazy("mealy:index")

    def form_invalid(self, form):
        raise ValidationError("Invalid form value", code='invalid')

    def form_valid(self, form):
        form.instance.meal_owner = self.request.user
        return super(NewMeal, self).form_valid(form)

@method_decorator(decs, name='dispatch')
class DeleteMeal(generic.edit.DeleteView):
    models              = Meal

    def get_queryset(self):
        return Meal.objects.filter( id=self.kwargs['pk'],
                                    meal_owner=self.request.user,
                                    dish__isnull=True)

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse("mealy:meal_detail",
                                    args=[self.get_object().id]))

    def get_success_url(self):
        return reverse("mealy:index")

@method_decorator(decs, name='dispatch')
class NewDish(generic.edit.CreateView):
    form_class  = DishForm

    def form_invalid(self, form):
        raise ValidationError("Invalid form value", code='invalid')

    def form_valid(self, form):
        form.instance.par_meal = Meal.objects.get( id=self.kwargs['meal_id'],
                                                meal_owner=self.request.user, )
        return super(NewDish, self).form_valid(form)

    def get_success_url(self):
        return reverse("mealy:meal_detail", args=[self.kwargs['meal_id']])

@method_decorator(decs, name='dispatch')
class DeleteDish(generic.edit.DeleteView):
    models              = Dish

    def get_queryset(self):
        return Dish.objects.filter( id=self.kwargs['pk'],
                                    par_meal__meal_owner=self.request.user,
                                    resource_ticket__isnull=True)

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse("mealy:dish_detail",
                                    args=[self.get_object().id]))

    def get_success_url(self):
        return reverse("mealy:meal_detail", args=[self.object.par_meal.id])

@method_decorator(decs, name='dispatch')
class DishView(generic.DetailView):
    def get_queryset(self):
        return Dish.objects.filter( id=self.kwargs['pk'],
                                    par_meal__meal_owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(DishView, self).get_context_data(**kwargs)
        context['tkt_form'] = TicketForm(self.request.user)
        return context

    def post(self, *args, **kwargs):
        form = TicketForm(self.request.user, self.request.POST)

        if form.is_valid():
            self.object = self.get_object()
            res_inst    = form.cleaned_data['resource_inst']
            uu          = form.cleaned_data['units_used']
            exhausted   = form.cleaned_data['exhausted']
            nt          = Resource_Ticket.objects.create_ticket(
                                        res_inst, uu, self.object, exhausted)
        else:
            raise Http404("Invalid form")
        return HttpResponseRedirect(
                        reverse("mealy:dish_detail", args=[self.object.id]))


@method_decorator(decs, name='dispatch')
class TypesOverview(generic.ListView):
    queryset            = Resource_Type.objects.order_by('r_parent')

@method_decorator(decs, name='dispatch')
class TypesView(generic.DetailView):
    slug_field          = "r_name"
    queryset            = Resource_Type.objects.all()

@method_decorator(decs, name='dispatch')
class StdInstListView(generic.ListView):
    queryset            = Standard_Inst.objects.order_by('inst_type')

@method_decorator(decs, name='dispatch')
class StdInstDetailView(generic.DetailView):
    queryset            = Standard_Inst.objects.all()

@method_decorator(decs, name='dispatch')
class InventView(generic.ListView):
    def get_queryset(self):
        objs = Resource_Inst.objects.filter(inst_owner=self.request.user)
        if not self.kwargs['showAll']:
            objs = objs.filter(exhausted=False)
        return objs.order_by('res_type', 'purchase_date')

    def get_context_data(self, **kwargs):
        context = super(InventView, self).get_context_data(**kwargs)
        context['types']    = Resource_Type.objects.all()
        context['showAll']  = self.kwargs['showAll']
        context['niForm']   = NewInstForm
        context['nisForm']  = NewInstStdForm(auto_id='newstdinstform_%s')
        return context

@method_decorator(decs, name='dispatch')
class DeleteTicket(generic.edit.DeleteView):
    models              = Resource_Ticket

    def get_queryset(self):
        return Resource_Ticket.objects.filter( id=self.kwargs['pk'], resource_inst__inst_owner=self.request.user)

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse("mealy:inv_detail",
                                    args=[self.get_object().resource_inst.id]))

    def get_success_url(self):
        return reverse("mealy:inv_detail", args=[self.object.resource_inst.id])

@login_required
@user_passes_test(other_checks)
def invent_detail(request, inst_id):
    inst = get_object_or_404(Resource_Inst, id=inst_id, inst_owner=request.user)

    if request.method == "POST":
        formType = request.POST['formtype']
        if formType == "finalise":
            defin = request.POST['finalisation']
            if defin == "final":
                inst.finalise()
            elif defin == "definal":
                inst.definalise()
            else:
                raise Http404("Finalisation invalid")
        elif formType == "attribchange":
            initf = inst.exhausted
            if initf:
                inst.definalise()
            newPrice = int(request.POST['price'])
            inst.change_price(newPrice)
            if initf:
                inst.finalise()
        else:
            raise Http404("We're not sure what form you submitted")
        return HttpResponseRedirect(reverse("mealy:inv_detail", args=[inst.id]))

    tickets = Resource_Ticket.objects.filter(resource_inst=inst).order_by('par_dish')
    template = loader.get_template("mealy/inv_detail.html")
    contDict =  {   'inst':         inst,
                    'attrib_form':  InstAttribForm,
                    'tickets':      tickets,
                }
    return HttpResponse(template.render(contDict, request))

@method_decorator(decs, name='dispatch')
class NewInst(generic.edit.CreateView):
    form_class  = NewInstForm
    success_url = reverse_lazy("mealy:inventory")

    def form_invalid(self, form):
        raise ValidationError("Invalid form value", code='invalid')

    def form_valid(self, form):
        form.instance.inst_owner        = self.request.user
        form.instance.unit_use_formal   = False
        return super(NewInst, self).form_valid(form)

@method_decorator(decs, name='dispatch')
class NewInstStd(generic.edit.CreateView):
    form_class  = NewInstStdForm
    success_url = reverse_lazy("mealy:inventory")

    def form_invalid(self, form):
        raise ValidationError("Invalid form value", code='invalid')

    def form_valid(self, form):
        form.instance.inst_owner        = self.request.user
        form.instance.unit_use_formal   = False
        form.instance.res_name          = form.cleaned_data['std_inst'].inst_name
        form.instance.res_type          = form.cleaned_data['std_inst'].inst_type
        form.instance.orig_unit         = form.cleaned_data['std_inst'].orig_units
        form.instance.amt_original      = form.cleaned_data['std_inst'].orig_amt
        form.instance.best_before       = form.cleaned_data['std_inst'].use_bestbef
        return super(NewInstStd, self).form_valid(form)

@login_required
@user_passes_test(other_checks)
def getStandardInst(request):
    inst = get_object_or_404(Standard_Inst, id=request.GET['id'])
    return HttpResponse(inst.show_fields())
