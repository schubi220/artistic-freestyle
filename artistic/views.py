from django.shortcuts import render
from artistic.models import Judge, Start, Value, Competition, Config, Event, Person
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from artistic.resultCalculators import FA # else won't find it later
from artistic import pdfview, resultCalculators
from django.conf import settings
from datetime import datetime
import re
from django.db.models import Q

# Create your views here.
@csrf_exempt
def code(request):
    code = request.POST.get('code', '')
    if code:
        try:
            j = Judge.objects.get(code__iexact=code.strip())
            request.session['accesscode'] = j.code
            if not (j.isActive or j.isReady):
                j.isActive = True
                j.save()
                return HttpResponseRedirect(reverse('artistic:input'))
            messages.warning(request, 'Ungültiger oder bereits verwendeter Code.')
        except Judge.DoesNotExist:
            messages.warning(request, 'Ungültiger oder bereits verwendeter Code.')

    return render(request, "artistic/code.html", {
        'code': code
    })

@csrf_exempt
def input(request):
    try:
        j = Judge.objects.get(code__iexact=request.session.get('accesscode'))
    except:
        return HttpResponseRedirect(reverse('artistic:code'))

    s = Start.objects.filter(competition=j.competition).order_by('order')

    if request.method == 'POST':
        for start in s:
            try:
                value = Value.objects.get(start=start, judge=j)
            except Value.DoesNotExist:
                value = Value(start=start, judge=j, values={})

            val = {}
            for i in [0,1,2]:
                v = request.POST.get(str(start.id)+'v'+str(i), '').replace(',', '.')
                try:
                    val[i] = float(v)
                except:
                    print('Not a float: ' + v)
            if val:
                value.values = val
                value.save()

        if 'ready' in request.POST:
            del request.session['accesscode']
            j.isReady = True
            j.save()
            messages.success(request, 'Wertung erfolgreich abgegeben, Danke :)')
            return HttpResponseRedirect(reverse('artistic:code'))
        return HttpResponseRedirect(reverse('artistic:input'))
    else:
        calc = getattr(eval('resultCalculators.'+j.competition.discipline), 'judgeResult')
        values = calc(s, j)

        return render(request, "artistic/input.html", {
            'judge': j,
            'starts': s,
            'values': values
        })


def free(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    cl = Competition.objects.filter(event__id=Config.get_config_value('event_id'))
    if not cl:
        messages.warning(request, 'Keine Altersklasse vorhanden.')
        return HttpResponseRedirect(reverse('admin:artistic_competition_add'))

    id = request.POST.get('judgeid', False)
    if id:
        j = Judge.objects.get(id=id)
        j.isActive = not j.isActive
        if not j.isActive:
            j.isReady = False
        j.save()

    id = request.POST.get('judgecorrect', False)
    if id and request.user.has_perm('artistic.change_value'):
    #if id:
        j = Judge.objects.get(id=id)
        j.isActive = True
        j.save()
        request.session['accesscode'] = j.code
        return HttpResponseRedirect(reverse('artistic:input'))

    actcompetition = request.POST.get('actcompetition', False)
    if actcompetition:
        request.session['actcompetition'] = actcompetition
    try:
        c = Competition.objects.get(id=request.session.get('actcompetition', Config.get_config_value('comp_id')), event__id=Config.get_config_value('event_id'))
    except:
        c = cl[0]
        s = Config.objects.get(key='comp_id')
        s.value = c.id
        request.session['actcompetition'] = c.id
        s.save()

    if request.POST.get('cntnew', False):
        for i in range(1, int(request.POST.get('cntnew'))+1):
            j = Judge(name='', possition='T'+str(i), type='T', competition=c)
            j.save()
            j = Judge(name='', possition='P'+str(i), type='P', competition=c)
            j.save()
        for i in range(1,3):
            j = Judge(name='', possition='D'+str(i), type='D', competition=c)
            j.save()

    j = Judge.objects.filter(competition=c)

    return render(request, "artistic/free.html", {
        'competitions': cl,
        'c': c,
        'judges': j
    })


def inputpdf(request, year = 2019):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition'))
    except:
        messages.warning(request, 'Keine Altersklasse gewählt')
        return HttpResponseRedirect(reverse('artistic:free'))

    s = Start.objects.filter(competition=c).order_by('order')
    j = Judge.objects.filter(competition=c)

    getattr(eval('pdfview.pdfinput'+str(year)), 'render')({'competiton': c, 'starts': s, 'judges': j})

    file_location = str(settings.BASE_DIR) + '/tmp/pdfinput.pdf'

    response = HttpResponse(open(file_location, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'filename='+c.name+'_sheed.pdf'
    return response


def select(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    cl = Competition.objects.filter(event__id=Config.get_config_value('event_id'))

    return render(request, "artistic/select.html", {
        'competitions': cl,
    })


def rate(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition'))
    except:
        messages.warning(request, 'Keine Altersklasse gewählt')
        return HttpResponseRedirect(reverse('artistic:free'))

    query = Q()
    v = request.GET.getlist('cid')
    if v:
        for id in v:
            query.add(Q(competition_id=id), Q.OR)
        c.name = request.GET.get('cname', 'mehrere Altersklassen')
    else:
        query.add(Q(competition=c), Q.AND)
    query.add(Q(isActive=True), Q.AND)
    s = Start.objects.filter(query).order_by('order')
    j = Judge.objects.filter(competition=c)

    calc = getattr(eval('resultCalculators.'+c.discipline), 'fullResult')
    result = calc(s, j)

    context = {
        'competiton': c,
        'starts': s,
        'judges': j,
        'result': result
    }
    pdfview.pdfresult(context)
    pdfview.pdfnotice(context)
    pdfview.pdfcertificate(context)
    return render(request, "artistic/rate.html", context)

def wrappdf(request, filename):
    if not request.user.is_authenticated:
        return HttpResponseNotFound('<h1>File not exist</h1>')
    c = Competition.objects.get(id=request.session.get('actcompetition'))

    file_location = str(settings.BASE_DIR) + '/tmp/pdf'+filename+'.pdf'

    try:
        response = HttpResponse(open(file_location, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'filename='+c.name+'_'+filename+'.pdf'
    except:
        response = HttpResponseNotFound('<h1>File not exist</h1>')

    return response


def read_csv(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    csvfile = request.POST.get('csvfile', False)
    date = request.POST.get('date')
    text = ''

    try:
        e = Event.objects.get(id=Config.get_config_value('event_id'))
    except Event.DoesNotExist:
        messages.warning(request, 'Keine Veranstaltung vorhanden.')
        return HttpResponseRedirect(reverse('admin:artistic_event_add'))

    if csvfile and re.match("^[0-9]{2}.[0-9]{2}.[0-9]{4}$", date):
        for row in csvfile.splitlines():
            data = row.split('\t')
            data[0] = data[0].strip()
            if data[0] == 'x' or data[0] == 'X':
                continue

            # anlegen Altersklasse
            if not data[0] or 99 < len(data[0]):
                messages.warning(request, data[2]+'#'+data[4]+' Altersklasse: '+data[0])
                continue
            c, created = Competition.objects.get_or_create(name__iexact=data[0], event=e, defaults={'name':data[0], 'minAge':0, 'maxAge':0, 'discipline':"FA"})

            # anlegen des Starts
            data[7] = date+' '+data[7].strip()
            data[2] = data[2].strip()
            if not re.match("^[0-9]{2}.[0-9]{2}.[0-9]{4} [0-9]{1,2}:[0-9]{2}$", data[7]) or not data[2].isnumeric():
                messages.warning(request, data[2]+'# Start: '+data[4])
                continue
            s = Start(order=data[2], competition=c, info={'titel': data[4].strip()}, time=datetime.strptime(data[7], '%d.%m.%Y %H:%M'))
            if int(data[1]) > 2:
                s.info['cnt'] = int(data[1])
                s.info['club'] = data[6].strip()
                s.save()
                text += s.order + '# ' + s.info['titel'] + '\r\n'
                continue

            # anlegen Personen
            people = data[5].split(' & ' if '&' in data[5] else ' und ')
            if len(people) != int(data[1]) or not data[5].strip():
                messages.warning(request, data[0]+'#'+data[2]+' Fahreranzahl: '+data[4])
                continue
            s.save()
            for person in people:
                club = data[6].split('/')[people.index(person)].strip() if len(people) > 1 and '/' in data[6] else data[6].strip()
                person = person.split(' ', 1)
                if len(person) != 2:
                    messages.warning(request, data[0]+'#'+data[2]+' Kein Nachname: '+data[6])
                    person[1] = ""
                p, created = Person.objects.get_or_create(firstname=person[0].strip(), lastname=person[1].strip(), event=e, defaults={'gender':'d', 'club':club, 'dateofbirth':datetime.strptime('0', '%H')})
                s.people.add(p)
            text += 'x\t' + s.order + '# ' + s.info['titel'] + '\r\n'

    return render(request, "artistic/import.html", {
        'text': text,
        'event': e,
    })


def choose_event(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    actevent = request.POST.get('actevent', False)
    if actevent:
        try:
            e = Event.objects.get(id=actevent)
            s = Config.objects.get(key='event_id')
            s.value = actevent
            s.save()
            messages.success(request, 'Varanstaltung: '+e.name+' ausgewählt.')
        except Event.DoesNotExist:
            messages.success(error, 'Fehler.')

    try:
        e = Event.objects.all()
    except Event.DoesNotExist:
        messages.warning(request, 'Keine Veranstaltung vorhanden.')
        return HttpResponseRedirect(reverse('admin:artistic_event_add'))

    return render(request, "artistic/choose_event.html", {
        'events': e,
    })


def displaySettings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    actcompetition = request.POST.get('actcompetition', False)
    if actcompetition:
        request.session['actcompetition'] = actcompetition

    actstart = request.POST.get('actstart', False)
    if actstart:
        s = Config.objects.get(key='start_id')
        s.value = actstart
        s.save()

    cl = Competition.objects.filter(event__id=Config.get_config_value('event_id'))
    if not cl:
        messages.warning(request, 'Keine Altersklasse vorhanden.')
        return HttpResponseRedirect(reverse('admin:artistic_competition_add'))

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition', Config.get_config_value('comp_id')))
    except:
        c = cl[0]

    s = Start.objects.filter(competition=c).order_by('order')

    return render(request, "artistic/displaySettings.html", {
        'competitions': cl,
        'c': c,
        'starts': s
    })

def displayBeamer(request):
    return render(request, "artistic/displayBeamer.html")

def displayMonitor(request):
    return render(request, "artistic/displayMonitor.html")

def displayMode(request):
    return HttpResponse(Config.get_config_value('start_id'))

def displayPushPull(request):
    act = Config.get_config_value('start_id')
    s = Start.objects.get(id=act)
    send = []
    send.append({
        'strnbr': s.order,
        'actors': s.competitors_names(),
        'titel': s.info['titel'],
        'club': s.competitors_clubs(),
        'cat': s.competition.name,
        'time': s.time.strftime("%H:%M"),
    })

    s = Start.objects.filter(time__gt=s.time).order_by('time')[:10]
    for start in s:
        send.append({
            'strnbr': start.order,
            'actors': start.competitors_names(),
            'titel': start.info['titel'],
            'club': start.competitors_clubs(),
            'cat': start.competition.name,
            'time': start.time.strftime("%H:%M"),
        })

    return JsonResponse(send, safe=False)
