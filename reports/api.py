from django.http import JsonResponse
import calendar
from reports.models import Reminder
import datetime
import time
from django.db.models import Q

def reshape(data, shape):
    i = 0
    res = []
    for row in range(shape[0]):
        res.append(data[i * shape[1]: (1 + i) * shape[1]])
        i += 1
    return res

def get_filters(start, end, field="date"):
    lt = field + '__lte'
    gt = field + '__gte'
    return(Q(Q(**{lt: end}) & Q(**{gt: start})))

class List2D(list):
    def __init__(self, *args, **kwargs):
        super(List2D, self).__init__(*args, **kwargs)
        self.is_flattened = False
    def flatten(self):
        res = []
        if self.is_flattened:
            return self
        for row in self:
            for i in row:
                res.append(i)
        self = res
        return res
    
    def reshape(self, shape):
        i = 0
        res = []
        for row in range(shape[0]):
            res.append(self[i * shape[1]: (1 + i) * shape[1]])
            i += 1
        return res

    @property
    def shape(self):
        if isinstance(self[0], list):
            return(len(self), len(self[0]))
        return len(self),


def get_month_data(array, user):
    '''benchmark later:
        1. requesting the DB every day
        2. requesting sorting the data
        3. requesting without sorting'''
    now = time.time()
    l2D = List2D(array)
    flat = l2D.flatten()
    shape = l2D.shape
    events = []
    filters = get_filters(flat[0], flat[len(flat)- 1])
    
    
    event_objs = Reminder.objects.filter(filters)
    
    events += [{
        'label': e.vehicle.name,
        'icon': 'truck',
        'date': e.date,
        'id': e.pk
    } for e in event_objs]

    active_recurring = Reminder.objects.filter(Q(active=True))
    
    for evt in active_recurring:
        for date in flat:
            if evt.repeat_on_date(date):
                events.append({
                    'label': evt.vehicle.name,
                    'icon': 'truck',
                    'date': date,
                    'id': evt.pk 
                })
    
    events = sorted(events, key=lambda x: x['date'])
    res = [{
        'date': i.strftime("%Y/%m/%d"),
        'day': i.day,
        'events' :[]
        } for i in flat]
    for e in events:
        count = 0
        for i in flat:
            if e['date'] == i:
                res[count]['events'].append(e)
                break
            else:
                count += 1 
    data = reshape(res, (shape))
    return  data

def get_month(request, year=None, month=None):
    year = int(year)
    month= int(month)
    current_date = datetime.date(year, month, 1)
    c = calendar.Calendar(calendar.MONDAY)
    array = c.monthdatescalendar(year, month)
    period_string = current_date.strftime('%B, %Y')
    user = request.user
    return JsonResponse({
        'period_string': period_string,
        'weeks': get_month_data(array, user)
    })