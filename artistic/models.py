from django.db import models
import random
import string
from datetime import date

# Create your models here.
DISCIPLINE_COICES = (
    ('TR', 'Track: Racing'),
    ('RR', 'Road: Races'),
    ('MR', 'Mountain Unicycling: Races'),
    ('MC', 'Mountain Unicycling: Cyclocross'),
    ('FA', 'Freestyle: Artistic'),
    ('FS', 'Freestyle: Standard Skill'),
    ('FX', 'Freestyle: X-Style'),
    ('UF', 'Urban: Flatland'),
    ('US', 'Urban: Street'),
    ('UT', 'Urban: Trials'),
    ('UP', 'Urban: Speed Trials'),
    ('UJ', 'Urban: Jumps'),
    ('TH', 'Team Sports: Hockey'),
    ('TB', 'Team Sports: Basketball'),
)


class Event(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField("Kürzel", help_text="Kürzel für die URL, nur Buchstaben, Zahlen und Striche, keine Leerzeichen, z.B. 'odm-steinach-2017'", unique=True)
    firstDay = models.DateField("Von")
    lastDay = models.DateField("Bis")
    description = models.TextField("beschreibung", blank=True)

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=100)
    minAge = models.IntegerField("minnimales Alter")
    maxAge = models.IntegerField("maximales Alter")
    discipline = models.CharField(max_length=2, choices=DISCIPLINE_COICES)

    event = models.ForeignKey(Event, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Person(models.Model):
    GENDER_CHOICES = (
        ("w", "weiblich"),
        ("m", "männlich"),
        ("d", "divers"),
    )
    firstname = models.CharField("Vorname", max_length=100)
    lastname = models.CharField("Nachname", max_length=100)
    gender = models.CharField("Geschlecht", max_length=1, choices=GENDER_CHOICES)

    email = models.EmailField("E-Mail")
    club = models.CharField("Verein oder Ort", max_length=100, blank=True)
    dateofbirth = models.DateField()

    street = models.CharField("Straße", max_length=255, blank=True, null=True)
    postcode = models.CharField("PLZ", max_length=20, blank=True, null=True)
    city = models.CharField("Stadt", max_length=100, blank=True, null=True)
    country = models.CharField("Land", max_length=2, default="DE", blank=True, null=True)

    event = models.ForeignKey(Event, on_delete=models.PROTECT)

    def get_age(self):
        today = date.today()
        return today.year - self.dateofbirth.year - ((today.month, today.day) < (self.dateofbirth.month, self.dateofbirth.day))

    def __str__(self):
        return self.firstname + ' ' + self.lastname


class Start(models.Model):
    order = models.IntegerField("Reihenfolge")
    people = models.ManyToManyField(Person, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    info = models.JSONField(default=dict())
    time = models.DateTimeField("Zeit des Starts")
    isActive = models.BooleanField("Started?", default=True)

    def competitors_names(self):
        people = self.people.all()
        if 'cnt' in self.info:
            return str(self.info['cnt'])+' Fahrer'
        if len(people) > 2:
            return str(len(people))+' Fahrer'
        return " und ".join(str(x) for x in people)
    def competitors_clubs(self):
        clubs = ""
        for x in self.people.all():
            if not x.club in clubs:
                clubs = clubs+", "+x.club
        return self.info['club'] if 'club' in self.info else clubs[2:]

    def __str__(self):
        return str(self.order) + '# ' + self.info['titel']


def generate_code():
    return "".join(random.choice(string.ascii_lowercase+string.digits) for i in range(8))

class Judge(models.Model):
    JUDGETYPE_CHOICES = (
        ("T", "Technik"),
        ("P", "Performance"),
        ("D", "Abstiege"),
    )
    name = models.CharField("Name", max_length=100)
    possition = models.CharField("Possition", max_length=2)
    type = models.CharField("Judge Art", max_length=1, choices=JUDGETYPE_CHOICES)
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    code = models.CharField(max_length=8, unique=True, default=generate_code)
    isActive = models.BooleanField("Eingeloggt?", default=False)

    def __str__(self):
        return str(self.possition) + '# ' + self.name


class Value(models.Model):
    start = models.ForeignKey(Start, on_delete=models.CASCADE)
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    values = models.JSONField(default=dict())

    class Meta:
        unique_together = ['start', 'judge']

class Config(models.Model):
    key = models.CharField("Key", max_length=10)
    value = models.CharField("Value", max_length=50)
