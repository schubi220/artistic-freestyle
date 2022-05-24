from django.shortcuts import render
from artistic.models import Judge, Start, Value, Competition, Config, Event
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from artistic import resultworker, pdfview
from django.conf import settings

# Create your views here.

def code(request):
    code = request.POST.get('code', '')
    if code:
        try:
            j = Judge.objects.get(code__iexact=code)
            request.session['accesscode'] = j.code
            if not j.isActive:
                j.isActive = True
                j.save()
                return HttpResponseRedirect(reverse('artistic:input'))
            messages.warning(request, 'Ungültiger oder bereits verwendeter Code.')
        except Judge.DoesNotExist:
            messages.warning(request, 'Ungültiger oder bereits verwendeter Code.')

    return render(request, "artistic/code.html", {
        'code': code
    })

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
                #print(str(start.id)+'v'+str(i)+' : '+v)
                try:
                    val[i] = float(v)
                except:
                    print('Not a float: ' + v)
            if val:
                value.values = val
                value.save()

        if 'ready' in request.POST:
            del request.session['accesscode']
            messages.success(request, 'Wertung erfolgreich abgegeben, Danke :)')
            return HttpResponseRedirect(reverse('artistic:code'))
        return HttpResponseRedirect(reverse('artistic:input'))
    else:
        calc = getattr(resultworker, 'calc' + j.type)
        values = calc(s, j)

        return render(request, "artistic/input.html", {
            'judge': j,
            'starts': s,
            'values': values
        })


def free(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('admin:login'), request.path))

    cl = Competition.objects.filter(event__id=Config.objects.get(key='event_id').value)

    id = request.POST.get('judgeid', False)
    if id:
        j = Judge.objects.get(id=id)
        j.isActive = not j.isActive
        j.save()

    id = request.POST.get('judgecorrect', False)
    if id:
        j = Judge.objects.get(id=id)
        j.isActive = True
        j.save()
        request.session['accesscode'] = j.code
        return HttpResponseRedirect(reverse('artistic:input'))

    actcompetition = request.POST.get('actcompetition', False)
    if actcompetition:
        request.session['actcompetition'] = actcompetition

    c = Competition.objects.get(id=request.session.get('actcompetition', 1))

    if request.POST.get('cntnew', False):
        for i in range(1, int(request.POST.get('cntnew'))+1):
            j = Judge(name='', possition='T'+str(i), type='T', competition=c)
            j.save()
            j = Judge(name='', possition='P'+str(i), type='P', competition=c)
            j.save()
        for i in [1,2]:
            j = Judge(name='', possition='D'+str(i), type='D', competition=c)
            j.save()

    j = Judge.objects.filter(competition=c)

    return render(request, "artistic/free.html", {
        'competitions': cl,
        'c': c,
        'judges': j
    })

def inputpdf(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('admin:login'), request.path))

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition'))
    except:
        messages.warning(request, 'Keine Altersklasse gewählt')
        return HttpResponseRedirect(reverse('artistic:free'))

    s = Start.objects.filter(competition=c).order_by('order')
    j = Judge.objects.filter(competition=c)

    pdfview.pdfinput({
        'starts': s,
        'judges': j
    })

    file_location = str(settings.BASE_DIR) + '/tmp/pdfinput.pdf'

    response = HttpResponse(open(file_location, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'filename='+c.name+'_sheed.pdf'
    return response


def rate(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('admin:login'), request.path))

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition'))
    except:
        messages.warning(request, 'Keine Altersklasse gewählt')
        return HttpResponseRedirect(reverse('artistic:free'))

    s = Start.objects.filter(competition=c, isActive=True).order_by('order')
    j = Judge.objects.filter(competition=c)

    values = {}
    judgetypes = {}
    result = {}
    result['full'] = {}
    for judge in j:
        if judge.type in judgetypes:
            judgetypes[judge.type] += 1
        else:
            judgetypes[judge.type] = 1
            result[judge.type] = {}

        calc = getattr(resultworker, 'calc' + judge.type)
        values[judge.possition] = calc(s, judge)

        for value in values[judge.possition]:
            if not value in result[judge.type]:
                result[judge.type][value] = 0
            result[judge.type][value] += values[judge.possition][value].values['result']

    sort = {}
    same = {}
    cnt = 0
    for start in s:
        for jtype in judgetypes:
            result[jtype][start.id] = result[jtype][start.id] / judgetypes[jtype]
        result['full'][start.id] = round(result['T'][start.id]*0.45 + result['P'][start.id]*0.45 + result['D'][start.id]*0.1, 4)
        a = str(round(result['T'][start.id], 4))[2:]
        a = str(result['full'][start.id])+a
        print(a)
        while a in sort:
            a += '0'
            same[a] = 0
        sort[a] = cnt
        cnt += 1

    pl = 1
    result['place'] = {}
    for res in sorted(sort, reverse=True):
        if res in same:
            if same[res] > 0:
                result['place'][sort[res]] = same[res]
            else:
                result['place'][sort[res]] = pl
            del same[res]
            same[res[0:-1]] = result['place'][sort[res]]
        else:
            result['place'][sort[res]] = pl
        pl += 1

    context = {
        'competiton': c,
        'starts': s,
        'judges': j,
        'judgetypes': judgetypes,
        'values': values,
        'result': result
    }
    pdfview.pdfdetail(context)
    pdfview.pdfresult(context)
    pdfview.pdfcertificate(context)
    return render(request, "artistic/rate.html", context)

def wrappdf(request, filename):
    if not request.user.is_authenticated:
        return HttpResponseNotFound('<h1>File not exist</h1>')
    c = Competition.objects.get(id=request.session.get('actcompetition'))

    file_location = str(settings.BASE_DIR) + '/tmp/'+filename+'.pdf'

    #    try:
    response = HttpResponse(open(file_location, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'filename='+c.name+'.pdf'
    #    except:
    #        response = HttpResponseNotFound('<h1>File not exist</h1>')

    return response


def read_csv(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('admin:login'), request.path))

    csvfile = request.POST.get('csvfile', False)
    text = ''

    e = Event.objects.get(id=Config.objects.get(key='event_id').value)

    if csvfile:
        for row in csvfile.splitlines():
            data = row.split('\t')

            if data[0] != 'x' and data[0] != 'X' and data[0] != '':

                # anlegen Altersklasse
                try:
                    c = Competition.objects.get(name__iexact=data[0])
                except Competition.DoesNotExist:
                    c = Competition(name=data[0], minAge=0, maxAge=0, discipline="FA", event=e)
                    c.save()
                # anlegen des Starts
                s = Start(order=data[2], competition=c, info=data[4], time=datetime.strptime('22-05-2022 '+data[7], '%d-%m-%Y %H:%M'))
                s.save()

                for person in data[5].split(' und '):
                    person = person.split(' ', 1)
                    try:
                        p = Person.objects.get(firstname=person[0], lastname=person[1], event=e)
                    except Person.DoesNotExist:
                        p = Person(firstname=person[0], lastname=person[1], gender='d', email='', club=data[6], dateofbirth=datetime.strptime('0', '%H'), event=e)
                    p.save()
                    s.people.add(p)

                text += s.order + '# ' + s.info + '\r\n'

    return render(request, "artistic/import.html", {
        'text': text
    })


def displaySettings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('%s?next=%s' % (reverse('admin:login'), request.path))

    actcompetition = request.POST.get('actcompetition', False)
    if actcompetition:
        request.session['actcompetition'] = actcompetition

    actstart = request.POST.get('actstart', False)
    if actstart:
        s = Config.objects.get(key='act_start')
        s.value = actstart
        s.save()

    try:
        c = Competition.objects.get(id=request.session.get('actcompetition'))
    except:
        messages.warning(request, 'Keine Altersklasse gewählt')
        return HttpResponseRedirect(reverse('artistic:free'))

    cl = Competition.objects.filter(event__id=Config.objects.get(key='event_id').value)
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
    return HttpResponse(Config.objects.get(key='act_start').value)

def displayPushPull(request):
    act = Config.objects.get(key='act_start').value
    s = Start.objects.filter(id__gte=act).order_by('time')[:10]

    send = []
    for start in s:
        send.append({
            'strnbr': start.order,
            'actors': start.competitors_names(),
            'titel': start.info,
            'club': start.competitors_clubs(),
            'cat': start.competition.name,
            'time': start.time.strftime("%H:%M"),
        })

    return JsonResponse(send, safe=False)
