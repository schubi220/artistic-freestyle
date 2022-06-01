from django.contrib import admin
from django.http import HttpResponseRedirect
from artistic.models import Event, Competition, Person, Start, Judge

class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('name', 'slug', 'description')}),
        ('Date information', {'fields': ('firstDay', 'lastDay')}),
    ]
    list_display = ('name', 'firstDay', 'lastDay')
    list_filter = ['firstDay']
    search_fields = ['name']


class CompetitionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'discipline', ('minAge', 'maxAge')]}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('event', )}),
    ]
    list_display = ('name', 'discipline', 'minAge', 'maxAge')
    list_filter = ['event']
    search_fields = ['name']


class PersonAdmin(admin.ModelAdmin):
    ordering = ['firstname', 'lastname']
    fieldsets = (
        ('Persönliche Daten', {'fields': (('firstname', 'lastname', 'gender'), ('email', 'club'), 'dateofbirth')}),
        ('Anschrift', {'fields': ('street', ('postcode', 'city'), 'country')}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('event', )}),
    )
    list_display = ('firstname', 'lastname', 'gender')
    list_filter = ['event']
    search_fields = ['firstname', 'lastname']


class StartAdmin(admin.ModelAdmin):
    ordering = ['time', 'competition', 'order']
    fieldsets = (
        (None, {'fields': ('order', 'people', 'competition', 'info', ('time', 'isActive'))}),
    )
    list_display = ('order', 'competitors_names', 'competitors_clubs', 'get_titel', 'competition', 'time', 'isActive')
    list_filter = ['competition']
    date_hierarchy = 'time'

    def competitors_names(self, inst):
        return inst.competitors_names()
    competitors_names.short_description = 'Name'
    def competitors_clubs(self, inst):
        return inst.competitors_clubs()
    competitors_clubs.short_description = 'Verein'
    def get_titel(self, inst):
        return inst.info['titel']
    get_titel.short_description = 'Titel'


class JudgeAdmin(admin.ModelAdmin):
    ordering = ['competition', 'possition']
    fieldsets = (
        (None, {'fields': ('name', ('possition', 'type'), 'competition', ('code', 'isActive'))}),
    )
    list_display = ('possition', 'name', 'type', 'competition', 'isActive')
    list_filter = ['competition']

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res


admin.site.register(Event, EventAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Start, StartAdmin)
admin.site.register(Judge, JudgeAdmin)
