from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.decorators import method_decorator
from .forms import MealForm, DishForm, TicketForm, TicketFormSet, InstAttribForm
import json, datetime, time

from .models import Resource_Type, Resource_Inst, Resource_Ticket, \
                TicketManager, Meal, Dish
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

@login_required
@user_passes_test(other_checks)
def meal_detail(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, meal_owner=request.user)

    dishes      = Dish.objects.filter(par_meal=meal).order_by('id')
    template    = loader.get_template("mealy/meal_detail.html")
    contDict    = { 'meal': meal, 'dishes': dishes, 'dish_form': DishForm }
    return HttpResponse(template.render(contDict, request))

@login_required
@user_passes_test(other_checks)
def meal_new(request):
    nm = Meal(
        meal_type   = request.POST["meal_type"],
        cons_time   = request.POST["meal_date"],
        meal_owner  = request.user,
    )
    nm.save()
    return HttpResponseRedirect(reverse("mealy:index"))

@login_required
@user_passes_test(other_checks)
def add_dish(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, meal_owner=request.user)

    if request.method == "POST":
        nd = Dish(cooking_style=request.POST['dish_style'], par_meal=meal)
        nd.save()
        return HttpResponseRedirect(
                        reverse("mealy:meal_detail", args=[meal_id]))
    else:
        template    = loader.get_template("mealy/add_dish.html")
        contDict     = { 'meal': meal, 'dish_form': DishForm }
        return HttpResponse(template.render(contDict, request))

@login_required
@user_passes_test(other_checks)
def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id, par_meal__meal_owner=request.user)

    if request.method == "POST":
        res_inst = Resource_Inst.objects.get(id=request.POST['resource_inst'],
                                                inst_owner=request.user)
        uu = float(request.POST['units_used'])
        exhausted = ('exhausted' in request.POST) and \
                    (request.POST['exhausted'] == 'on')

        nt = Resource_Ticket.objects.create_ticket(
                        res_inst, uu, dish, exhausted)
        return HttpResponseRedirect(
                        reverse("mealy:dish_detail", args=[dish.id]))

    tickets = Resource_Ticket.objects.filter(par_dish=dish).order_by('id')
    contDict    = { 'dish': dish, 'ticket_form': TicketForm }
    if len(tickets):
        contDict['tickets'] = tickets
    template    = loader.get_template("mealy/dish_detail.html")
    return HttpResponse(template.render(contDict, request))

@method_decorator(decs, name='dispatch')
class TypesView(generic.ListView):
    template_name       = "mealy/types.html"
    context_object_name = "type_list"
    queryset            = Resource_Type.objects.order_by('r_parent')

@method_decorator(decs, name='dispatch')
class TypesDetailView(generic.DetailView):
    template_name       = "mealy/types_detail.html"
    context_object_name = "r_type"
    slug_field          = "r_name"
    queryset            = Resource_Type.objects.all()

@login_required
@user_passes_test(other_checks)
def invent(request, showAll):
    if not showAll:
        inv = Resource_Inst.objects.filter(inst_owner=request.user.id,
                        exhausted=False).order_by('res_type', 'purchase_date')
    else:
        inv = Resource_Inst.objects.filter(inst_owner=request.user.id).order_by(
                        'res_type', 'purchase_date')
    template = loader.get_template("mealy/inventory.html")
    contDict = {    'items':    inv,
                    'types':    Resource_Type.objects.filter(),
                    'showAll':  showAll,
                }
    return HttpResponse(template.render(contDict, request))

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
        elif formType == "cancelticket":
            ticketId = int(request.POST['ticketid'])
            try:
                ticket = Resource_Ticket.objects.get(id=ticketId,
                                                        resource_inst=inst)
            except Resource_Ticket.DoesNotExist:
                raise Http404("Invalid ticket")
            initf = inst.exhausted
            if initf:
                inst.definalise()
            ticket.remove()
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

@login_required
@user_passes_test(other_checks)
def invent_new_item(request):
    #   Add a new object
    ni = Resource_Inst(
        res_name        = request.POST["res_name"],
        res_type        = Resource_Type.objects.get(
                            r_name=request.POST["res_type"]),
        unit_use_formal = "use_formal" in request.POST,
        units_original  = request.POST["orig_units"],
        amt_original    = request.POST["qty"],
        price           = request.POST["price"],
        best_before     = not("use_bb" in request.POST
                            and request.POST["use_bb"] == "False"),
        best_bef_date   = request.POST["bb_date"],
        purchase_date   = request.POST["purchase_date"],
        inst_owner      = request.user, )
    ni.save()
    return HttpResponseRedirect(reverse("mealy:inventory"))

@login_required
@user_passes_test(other_checks)
def about(request):
    return render(request, "mealy/about.html")
