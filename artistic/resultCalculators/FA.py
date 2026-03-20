from artistic.models import Value, Judge
from django.db.models.query import QuerySet
import math

def judgeResult(s: QuerySet, judge: Judge):
    values = {}
    sum = 0
    sort = []
    for start in s:
        try:
            values[start.id] = Value.objects.get(start=start, judge__possition=judge.possition)
        except Value.DoesNotExist:
            values[start.id] = Value(start=start, judge=judge, values={0:0,1:0,2:0,'total':0})

        if judge.type == 'D':
            dismount_scores = values[start.id].values
            drivers_count = dismount_scores.get('2', 0)
            base = dismount_scores.get('0', 0) * 0.5 + dismount_scores.get('1', 0)
            
            score = 10 - (base / (math.sqrt(drivers_count) if drivers_count > 2 else 1))
            dismount_scores['total'] = max(0, score)

        else:
            values[start.id].values['total'] = values[start.id].values.get('0',0)+values[start.id].values.get('1',0)+values[start.id].values.get('2',0)

        a = str(values[start.id].values['total'])
        while a in sort: a += '0'
        sort.append(float(a))

    sort.sort(reverse=True)
    for start in s:
        values[start.id].values['place'] = sort.index(values[start.id].values['total']) + 1

    return values

def fullResult(s: QuerySet, j: QuerySet, remove=False):
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
                result['full'][judge.type][i] = Value(start=res.start, judge=res.judge, values={0:0,1:0,2:0,'total':0})
                result['full'][judge.type][i].values['remove'] = {}
            result['full'][judge.type][i].values['total'] += res.values.get('total',0)
            result['full'][judge.type][i].values['remove'][judge.possition] = res.values.get('total',0)
    
    sum = 0
    for type in result['full']:
        count = len(result[type])
        for i in result['full'][type]:
            if remove and count > 2:
                result['full'][type][i].values['min'] = min(result['full'][type][i].values['remove'], key=result['full'][type][i].values['remove'].get)
                result['full'][type][i].values['max'] = max(result['full'][type][i].values['remove'], key=result['full'][type][i].values['remove'].get)
                result['full'][type][i].values['total'] -= result['full'][type][i].values['remove'][result['full'][type][i].values['min']]
                result['full'][type][i].values['total'] -= result['full'][type][i].values['remove'][result['full'][type][i].values['max']]
                result['full'][type][i].values['total'] /= count-2
            else:
                result['full'][type][i].values['total'] /= count

    result['full']['full'] = {}
    sort = {}
    for i in result['full']['D']:
        res = (result['full']['T'][i].values['total']*0.45/30+result['full']['P'][i].values['total']*0.45/30+result['full']['D'][i].values['total']*0.1/10)*100
        a = str(res)
        while a in sort: a += '0'
        sort[a] = i

    pl = 1
    for res in sorted(sort, reverse=True):
        result['full']['full'][sort[res]] = {'total': float(res), 'place': pl}
        if res[-1] != '0':
            pl += 1

    return result
