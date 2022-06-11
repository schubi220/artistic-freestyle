from django.contrib import admin
from django.http import HttpResponseRedirect
from artistic.models import Event, Competition, Person, Start, Judge, Config


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('name', 'slug', 'description')}),
        ('Date information', {'fields': ('firstDay', 'lastDay')}),
    ]
    list_display = ('name', 'firstDay', 'lastDay')
    list_filter = ['firstDay']
    search_fields = ['name']
    actions = None


class EventFilterModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        q = request.GET.copy()
        q['event__id__exact'] = Config.objects.get(key='event_id').value
        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(EventFilterModelAdmin,self).changelist_view(request, extra_context=extra_context)

class CompetitionAdmin(EventFilterModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'discipline', ('minAge', 'maxAge')]}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('event', )}),
    ]
    list_display = ('name', 'discipline', 'minAge', 'maxAge')
    search_fields = ['name']


class PersonAdmin(EventFilterModelAdmin):
    ordering = ['firstname', 'lastname']
    fieldsets = (
        ('Persönliche Daten', {'fields': (('firstname', 'lastname', 'gender'), ('email', 'club'), 'dateofbirth')}),
        ('Anschrift', {'fields': ('street', ('postcode', 'city'), 'country')}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('event', )}),
    )
    list_display = ('firstname', 'lastname', 'gender')
    search_fields = ['firstname', 'lastname']


class CompetitionFilterModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        if 'competition__id__exact' not in request.GET:
            q = request.GET.copy()
            q['competition__id__exact'] = Config.objects.get(key='comp_id').value
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(CompetitionFilterModelAdmin,self).changelist_view(request, extra_context=extra_context)

class CompetitionFilter(admin.SimpleListFilter):
    title = 'competition'
    parameter_name = 'competition__id__exact'

    def lookups(self, request, model_admin):
        cl = set([c.competition for c in model_admin.model.objects.filter(competition__event__id=Config.objects.get(key='event_id').value)])
        print(cl)
        return [(c.id, c.name) for c in cl]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(competition__id__exact=self.value())


class StartAdmin(CompetitionFilterModelAdmin):
    ordering = ['time', 'competition', 'order']
    fieldsets = (
        (None, {'fields': ('order', 'people', 'competition', 'info', ('time', 'isActive'))}),
    )
    list_display = ('order', 'competitors_names', 'competitors_clubs', 'get_titel', 'competition', 'time', 'isActive')
    list_filter = [CompetitionFilter]
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


class JudgeAdmin(CompetitionFilterModelAdmin):
    ordering = ['competition', 'possition']
    fieldsets = (
        (None, {'fields': ('name', ('possition', 'type'), 'competition', ('code', 'isActive'))}),
    )
    list_display = ('possition', 'name', 'type', 'competition', 'isActive')
    list_filter = [CompetitionFilter]

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
