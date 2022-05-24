from django.contrib import admin

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
    fieldsets = (
        ('Persönliche Daten', {'fields': (('firstname', 'lastname', 'gender'), ('email', 'club'), 'dateofbirth')}),
        ('Anschrift', {'fields': ('street', ('postcode', 'city'), 'country')}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('event', )}),
    )
    list_display = ('firstname', 'lastname', 'gender')
    list_filter = ['event']
    search_fields = ['firstname', 'lastname']


class StartAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('order', 'people', 'competition', 'info', ('time', 'isActive'))}),
    )
    list_display = ('order', 'competitors_names', 'info', 'competition', 'time', 'isActive')
    list_filter = ['competition']

    def competitors_names(self, inst):
        return ", ".join(str(x) for x in inst.people.all())
    competitors_names.short_description = 'Teilnehmer'


class JudgeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', ('possition', 'type'), 'competition', ('code', 'isActive'))}),
    )
    list_display = ('possition', 'name', 'type', 'competition', 'isActive')
    list_filter = ['competition']


admin.site.register(Event, EventAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Start, StartAdmin)
admin.site.register(Judge, JudgeAdmin)
