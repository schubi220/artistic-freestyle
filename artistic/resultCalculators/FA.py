from artistic.models import Value, Judge
from django.db.models.query import QuerySet
import math

def judgeResult(s: QuerySet, judge: Judge):
    values = {}
    sum = 0
    for start in s:
        try:
            values[start.id] = Value.objects.get(start=start, judge__possition=judge.possition)
        except Value.DoesNotExist:
            values[start.id] = Value(start=start, judge=judge)
        if judge.type == 'D':
            values[start.id].values['summe'] = (10-(values[start.id].values.get('0',0)*0.5+values[start.id].values.get('1',0))) if values[start.id].values.get('2',0) < 2 else (10-((values[start.id].values.get('0',0)*0.5+values[start.id].values.get('1',0))/math.sqrt(values[start.id].values.get('2',0))))
        else:
            values[start.id].values['summe'] = values[start.id].values.get('0',0)+values[start.id].values.get('1',0)+values[start.id].values.get('2',0)
        sum += values[start.id].values['summe']

    sort = []
    for start in s:
        values[start.id].values['result'] = (values[start.id].values['summe'] / sum) if sum > 0 else 0
        a = str(values[start.id].values['result'])
        while a in sort: a += '0'
        sort.append(float(a))

    sort.sort(reverse=True)
    for start in s:
        values[start.id].values['place'] = sort.index(values[start.id].values['result']) + 1

    return values

def fullResult(s: QuerySet, j: QuerySet):
    result = {}
    result['full'] = {}

    for judge in j:
        if not judge.type in result:
            result[judge.type] = {}
            result['full'][judge.type] = {}

        result[judge.type][judge.possition] = judgeResult(s, judge)

        for i in result[judge.type][judge.possition]:
            res = result[judge.type][judge.possition][i]

            if not i in result['full'][judge.type]:
                result['full'][judge.type][i] = Value(start=res.start, judge=res.judge, values={0:0,1:0,2:0,'summe':0,'result':0})

            result['full'][judge.type][i].values[0] += res.values.get('0',0)
            result['full'][judge.type][i].values[1] += res.values.get('1',0)
            result['full'][judge.type][i].values[2] += res.values.get('2',0)
            result['full'][judge.type][i].values['summe'] += res.values.get('summe',0)
            result['full'][judge.type][i].values['result'] += res.values.get('result',0)
    
    sum = 0
    for type in result['full']:
        count = len(result[type])
        for i in result['full'][type]:
            result['full'][type][i].values[0] /= count
            result['full'][type][i].values[1] /= count
            result['full'][type][i].values[2] /= count
            
            result['full'][type][i].values['summe'] /= count
            result['full'][type][i].values['result'] /= count

            if type == 'D':
                result['full'][type][i].values['summe'] = (10-(result['full'][type][i].values.get(0,0)*0.5+result['full'][type][i].values.get(1,0))) if result['full'][type][i].values.get(2,0) < 2 else (10-((result['full'][type][i].values.get(0,0)*0.5+result['full'][type][i].values.get(1,0))/math.sqrt(result['full'][type][i].values.get(2,0))))
                sum += result['full'][type][i].values['summe']

    result['full']['full'] = {}
    sort = []
    for i in result['full']['D']:
        result['full']['D'][i].values['result'] = (result['full']['D'][i].values['summe'] / sum) if sum > 0 else 0

        result['full']['full'][i] = {'result': result['full']['T'][i].values['result']*0.45+result['full']['P'][i].values['result']*0.45+result['full']['D'][i].values['result']*0.1}
        a = str(result['full']['full'][i]['result'])
        while a in sort: a += '0'
        sort.append(float(a))

    sort.sort(reverse=True)
    for i in result['full']['D']:
        result['full']['full'][i]['place'] = sort.index(result['full']['full'][i]['result']) + 1


    return result
