from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from .forms import MealForm, DishForm, TicketForm, TicketFormSet
import json, datetime, time

from .models import Resource_Type, Resource_Inst, Resource_Ticket, \
                TicketManager, Meal, Dish
# Create your views here.

SEMI_OPEN_STATE_THRESHOLD = 10

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    fifth_jan = datetime.date(iso_year, 1, 5)
    _, fifth_jan_week, fifth_jan_day = fifth_jan.isocalendar()
    return fifth_jan + datetime.timedelta(days=iso_day-fifth_jan_day,
                                            weeks=iso_week-fifth_jan_week)

@login_required
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
                tot += meal.meal_cost
                mc += 1
                opensum += meal.open_cost
            weekMeals[w] = [ (u"%s \xA3%.2f" % (meal.meal_type[0],
                                meal.meal_cost/100),
                                reverse("mealy:meal_detail", args=(meal.id,)),
                                meal.open_cost > SEMI_OPEN_STATE_THRESHOLD)
                                for meal in weekMeals[w]]
            # weekMeals[0] = (monday) [ ("L 2.77", det_link, T), ... ]
            weekMeals[w] = [iso_to_gregorian(e[0], e[1], w+1).strftime("%b %d"),
                                weekMeals[w]]
            # weekMeals[0] = [ "Mar 14", [ ("L...", det_link, T), ... ] ]
            weekMeals[w][1].sort()
        weekMeals.append(["", [(u"T \xA3%.2f (%.2f)" % (tot/100, opensum/100),
                                    False, ),
                            (u"A \xA3%.2f (%.2f)" %
                                    (tot/100/mc, opensum/100/mc), False, )]])
        cal[e] = weekMeals
    cal = sorted(list(cal.items()), reverse=True)

    template    = loader.get_template("mealy/meals.html")
    contDict =  {   'meal_list': meal_list,
                    'mtypes': Meal.MEAL_TYPES,
                    'meal_form': MealForm,
                    'user':     request.user,
                    'cal_meals': cal }
    return HttpResponse(template.render(contDict, request))

@login_required
def meal_detail(request, meal_id):
    try:
        meal = Meal.objects.get(id=meal_id, meal_owner=request.user)
    except Meal.DoesNotExist:
        raise Http404("Meal does not exist")

    dishes      = Dish.objects.filter(par_meal=meal).order_by('id')
    template    = loader.get_template("mealy/meal_detail.html")
    contDict    = { 'meal': meal, 'dishes': dishes, 'dish_form': DishForm }
    return HttpResponse(template.render(contDict, request))

@login_required
def meal_new(request):
    nm = Meal(
        meal_type   = request.POST["meal_type"],
        cons_time   = request.POST["meal_date"],
        meal_owner  = request.user,
    )
    nm.save()
    return HttpResponseRedirect(reverse("mealy:index"))

@login_required
def add_dish(request, meal_id):
    try:
        meal = Meal.objects.get(id=meal_id, meal_owner=request.user)
    except Meal.DoesNotExist:
        raise Http404("Meal does not exist")

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
def dish_detail(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id, par_meal__meal_owner=request.user)
    except Dish.DoesNotExist:
        raise Http404("Dish does not exist")

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

@login_required
def types(request):
    type_list = Resource_Type.objects.order_by('r_parent')
    #output = ', '.join([t.r_name for t in type_list])
    template = loader.get_template("mealy/types.html")
    contDict = { 'type_list': type_list }
    return HttpResponse(template.render(contDict, request))

@login_required
def types_detail(request, res_name):
    try:
        ex_type = Resource_Type.objects.get(r_name=res_name)
    except Resource_Type.DoesNotExist:
        raise Http404("Resource Type does not exist.")
    #type_list = Resource_Type.objects.filter(r_parent=ex_type)
    type_list = ex_type.resource_type_set.all()
    template = loader.get_template("mealy/types_detail.html")
    contDict = {    "res_name": ex_type.r_name,
                    "type_list": type_list,
                    "par": ex_type.r_parent if ex_type.r_parent else None
                }
    return HttpResponse(template.render(contDict, request))

@login_required
def invent(request):
    inv = Resource_Inst.objects.filter(inst_owner=request.user.id, exhausted=False).order_by('res_type', 'purchase_date')
    template = loader.get_template("mealy/inventory.html")
    contDict = {    'items': inv,
                    'types': Resource_Type.objects.filter()
                }
    return HttpResponse(template.render(contDict, request))

@login_required
def invent_detail(request, inst_id):
    try:
        inst = Resource_Inst.objects.get(id=inst_id, inst_owner=request.user)
    except Resource_Inst.DoesNotExist:
        raise Http404("Instance does not exist")

    template = loader.get_template("mealy/inv_detail.html")
    contDict = { 'inst': inst }
    return HttpResponse(template.render(contDict, request))

@login_required
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
