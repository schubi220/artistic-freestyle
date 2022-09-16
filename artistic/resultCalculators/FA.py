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
