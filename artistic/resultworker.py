from artistic.models import Value, Judge
from django.db.models.query import QuerySet
import math

def calcT(s: QuerySet, judge: Judge):
    return __calc(s, judge, "values[start.id].values.get('0',0)+values[start.id].values.get('1',0)+values[start.id].values.get('2',0)")

def calcP(s: QuerySet, judge: Judge):
    return __calc(s, judge, "values[start.id].values.get('0',0)+values[start.id].values.get('1',0)+values[start.id].values.get('2',0)")

def calcD(s: QuerySet, judge: Judge):
    return __calc(s, judge, "(10-(values[start.id].values.get('0',0)*0.5+values[start.id].values.get('1',0))) if values[start.id].values.get('2',0) < 2 else (10-((values[start.id].values.get('0',0)*0.5+values[start.id].values.get('1',0))/math.sqrt(values[start.id].values.get('2',0))))")


def __calc(s: QuerySet, judge: Judge, calculate):
    values = {}
    summe = 0

    for start in s:
        try:
            values[start.id] = Value.objects.get(start=start, judge__possition=judge.possition)
        except Value.DoesNotExist:
            values[start.id] = Value(start=start, judge=judge)
        values[start.id].values['summe'] = eval(calculate)
        summe += values[start.id].values['summe']

    sort = {}
    same = {}
    for start in s:
        if summe > 0:
            values[start.id].values['result'] = values[start.id].values['summe'] / summe
        else:
            values[start.id].values['result'] = 0
        a = str(values[start.id].values['result'])
        while a in sort:
            a += '0'
            same[a] = 0
        sort[a] = start.id

    pl = 1
    for res in sorted(sort, reverse=True):
        if res in same:
            if same[res] > 0:
                values[sort[res]].values['place'] = same[res]
            else:
                values[sort[res]].values['place'] = pl
                del same[res]
            same[res[0:-1]] = values[sort[res]].values['place']
        else:
            values[sort[res]].values['place'] = pl
        pl += 1

    return values
