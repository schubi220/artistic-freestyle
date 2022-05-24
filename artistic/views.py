from django.shortcuts import render
from artistic.models import Judge, Start, Value
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from artistic import resultworker

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
