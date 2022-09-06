from django.conf import settings
from reportlab.lib.pagesizes import A3, landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from artistic.models import Judge, Config, Event
import math
import datetime

def pdfdetail(context):
    c = SimpleDocTemplate(str(settings.BASE_DIR) + '/tmp/pdfdetail.pdf', pagesize=landscape(A3), rightMargin=56, leftMargin=56, topMargin=56, bottomMargin=56)
    pagecontext = []
    sample_style_sheet = getSampleStyleSheet()
    pagecontext.append(Paragraph(context['competiton'].name, sample_style_sheet['Heading1']))
    sample_style_sheet['Heading2'].spaceBefore = 25

    for jtype in context['judgetypes']:
        pagecontext.append(Paragraph([i[1] for i in Judge.JUDGETYPE_CHOICES if i[0] == jtype][0], sample_style_sheet['Heading2']))
        data =[]
        row = ['#', 'Name', 'Verein']
        row.append(jtype)
        for judge in context['judges']:
            if judge.type == jtype:
                row.append(judge.possition)
                row.append('')
                row.append('1')
                row.append('2')
                row.append('3')
        data.append(row)

        for start in context['starts']:
            row = []
            row.append(start.order)
            row.append(start.competitors_names()[0:32])
            row.append(start.competitors_clubs()[0:18])
            row.append(f"{context['result'][jtype][start.id] * 100.0:.{2}f}%")
            for judge in context['judges']:
                if judge.type == jtype:
                    row.append(context['values'][judge.possition][start.id].values['place'])
                    row.append(f"{context['values'][judge.possition][start.id].values['result'] * 100.0:.{2}f}%")
                    row.append(context['values'][judge.possition][start.id].values.get('0'))
                    row.append(context['values'][judge.possition][start.id].values.get('1'))
                    row.append(context['values'][judge.possition][start.id].values.get('2'))
            data.append(row)

        t = Table(data, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.yellow),
            ('LINEBELOW',(0,0),(-1,0),2,colors.black),
            ('BACKGROUND',(0,0),(-1,0),colors.yellow)
        ]))
        pagecontext.append(t)

#    pagecontext.append(PageBreak())
    pagecontext.append(Paragraph("Gesamt", sample_style_sheet['Heading2']))
    data =[]
    row = ['#', 'Name', 'Verein', 'Gesamt']
    for jtype in context['judgetypes']:
        row.append(jtype)
        for judge in context['judges']:
            if judge.type == jtype:
                row.append(judge.possition)
    data.append(row)

    for start in context['starts']:
        row = []
        row.append(start.order)
        row.append(start.competitors_names()[0:32])
        row.append(start.competitors_clubs()[0:18])
        row.append(f"{context['result']['full'][start.id] * 100.0:.{2}f}%")
        for jtype in context['judgetypes']:
            row.append(f"{context['result'][jtype][start.id] * 100.0:.{2}f}%")
            for judge in context['judges']:
                if judge.type == jtype:
                    row.append(str(context['values'][judge.possition][start.id].values['place']) +" "+ f"{context['values'][judge.possition][start.id].values['result'] * 100.0:.{2}f}%")
        data.append(row)

    t = Table(data, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.yellow),
        ('LINEBELOW',(0,0),(-1,0),2,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.yellow)
    ]))
    pagecontext.append(t)

    c.multiBuild(pagecontext, canvasmaker=FooterDetail)

class FooterDetail(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        self.saveState()
        self.setLineWidth(0.25)
        self.line(595.275590551, 841.8897637795277, 595.275590551, 826.8897637795277)
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont("Helvetica", 6)
        self.drawString(20, 25, Event.objects.get(id=Config.objects.get(key='event_id').value).name)
        self.drawCentredString(595.275590551, 25, "Seite %s von %s" % (self._pageNumber, page_count))
        self.drawRightString(1150.551181102, 25, 'Ergebnis vom: '+datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        self.restoreState()

def pdfresult(context):
    c = SimpleDocTemplate(str(settings.BASE_DIR) + '/tmp/pdfresult.pdf', pagesize=A4, rightMargin=56, leftMargin=56, topMargin=56, bottomMargin=56)
    pagecontext = []
    sample_style_sheet = getSampleStyleSheet()
    data =[]

    sample_style_sheet['Heading1'].alignment = 1
    pagecontext.append(Paragraph(Event.objects.get(id=Config.objects.get(key='event_id').value).name, sample_style_sheet['Heading1']))
    pagecontext.append(Paragraph(context['competiton'].name, sample_style_sheet['Heading2']))

    row = ['Platz', 'Name', 'Verein', 'Titel']
    for jtype in context['judgetypes']:
        row.append(jtype)
    row.append('Ergebniss')
    data.append(row)

    for cnt in context['result']['place']:
        start = context['starts'][cnt]
        row = []
        row.append(context['result']['place'][cnt])
        row.append(Paragraph(start.competitors_names(), sample_style_sheet['Normal']))
        row.append(Paragraph(start.competitors_clubs(), sample_style_sheet['Normal']))
        row.append(Paragraph(start.info['titel'], sample_style_sheet['Normal']))
        for jtype in context['judgetypes']:
            row.append(f"{context['result'][jtype][start.id] * 100.0:.{2}f}%")
        row.append(f"{context['result']['full'][start.id] * 100.0:.{2}f}%")
        data.append(row)

    t = Table(data, colWidths=(None, 35*mm, 33*mm, 48*mm, None, None, None, None))
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.yellow),
        ('LINEBELOW',(0,0),(-1,0),2,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.yellow)
    ]))
    pagecontext.append(t)

    c.multiBuild(pagecontext, canvasmaker=FooterResult)

class FooterResult(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        self.saveState()
        self.setLineWidth(0.25)
        self.line(0, 420.94488189, 15, 420.94488189)
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont("Helvetica", 6)
        self.drawString(20, 25, Event.objects.get(id=Config.objects.get(key='event_id').value).name)
        self.drawCentredString(297.637795276, 25, "Seite %s von %s" % (self._pageNumber, page_count))
        self.drawRightString(575.2755905511812, 25, 'Ergebnis vom: '+datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        self.restoreState()


def pdfcertificate(context):
    c = canvas.Canvas(str(settings.BASE_DIR) + '/tmp/pdfcertificate.pdf', pagesize=A4)
    data =[]

    row = ['Platz', 'Name', 'Verein', 'Titel']
    for jtype in context['judgetypes']:
        row.append(jtype)
    row.append('Ergebniss')
    data.append(row)

    x = 105 * mm
    y = 200 * mm
    for cnt in context['result']['place']:
        start = context['starts'][cnt]
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(x,y, start.competitors_names())
        c.setFont("Helvetica", 16)
        c.drawCentredString(x,y-28.34645669291339, start.competitors_clubs())
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(x,y-79.37007874015748, str(context['result']['place'][cnt]) + '. Platz')
        c.setFont("Helvetica", 16)
        c.drawCentredString(x,y-124.7244094488189, context['competiton'].name)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(x,y-147.40157480314963, start.info['titel'])
        c.showPage()

    c.save()

class pdfinput2019:
    def render(context):
        c = canvas.Canvas(str(settings.BASE_DIR) + '/tmp/pdfinput.pdf', pagesize=landscape(A4))

        pages = math.ceil(context['starts'].count()/3)
        for judge in context['judges']:
            page = 1
            cnt = 0
            pdfinput2019.__headerfooter(c, judge, [page, pages])
            c.translate(0, 137*mm)
            for start in context['starts']:
                if cnt == 3:
                    cnt = 0
                    page += 1
                    c.showPage()
                    pdfinput2019.__headerfooter(c, judge, [page, pages])
                    c.translate(0, 137*mm)
                pdfinput2019.__frame(c, start)
                getattr(pdfinput2019, "print" + judge.type)(c)
                c.translate(0, -59*mm)
                cnt += 1
            c.showPage()

        c.save()

    def __headerfooter(c, judge, page):
        c.setLineWidth(0.25)
        c.line(420.94488189, 595.275590551181, 420.94488189, 580.275590551181)
        c.setFont('Helvetica-Bold', 14)
        c.drawString(9*mm, 200*mm, 'Technik')
        c.setFont('Helvetica', 10)
        c.drawString(140*mm, 200*mm, 'Disziplin: ' + judge.competition.name)
        c.drawString(195*mm, 200*mm, 'Code: ' + judge.code)
        c.drawString(232*mm, 200*mm, 'Jury: ' + judge.possition)

        c.setFont('Helvetica', 6)
        c.drawCentredString(420.94488189, 20, 'Seite: '+str(page[0])+' von '+str(page[1]))

    def __frame(c, start):
        c.setLineWidth(2)
        c.rect(9*mm, 0, 49*mm, 56*mm)
        c.rect(58*mm, 0, 226*mm, 56*mm)
        c.setLineWidth(1)
        c.setFont('Helvetica', 10)
        c.drawString(12*mm, 49*mm, 'Name:')
        if len(start.competitors_names()) > 24:
            c.drawString(12*mm, 43*mm, start.competitors_names()[0:24])
            c.drawString(12*mm, 40*mm, start.competitors_names()[24:50])
        else:
            c.drawString(12*mm, 40*mm, start.competitors_names()[0:24])
        c.line(12*mm, 39*mm, 55*mm, 39*mm)
        c.drawString(12*mm, 29*mm, 'Kürtitel:')
        if len(start.info['titel']) > 24:
            c.drawString(12*mm, 23*mm, start.info['titel'][0:24])
            c.drawString(12*mm, 20*mm, start.info['titel'][24:50])
        else:
            c.drawString(12*mm, 20*mm, start.info['titel'][0:24])
        c.line(12*mm, 19*mm, 55*mm, 19*mm)

    def printT(c):
        c.setFillColorRGB(0.88,0.94,0.85)
        c.setStrokeColorRGB(1,1,1)
        c.rect(60*mm, 48*mm, 189*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.line(60*mm, 48*mm, 60*mm, 53*mm)
        c.line(249*mm, 48*mm, 249*mm, 53*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(61*mm, 49*mm, 'Anzahl und Schwierigkeit der Tricks und Übergänge')
        c.setFont('Helvetica', 7)
        c.drawString(61*mm, 45*mm, 'einfache Basics')
        c.rect(60*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(60*mm, 21*mm, 31.5*mm, 23*mm)
        c.drawString(92.5*mm, 45*mm, 'höhere Basics')
        c.rect(91.5*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(91.5*mm, 21*mm, 31.5*mm, 23*mm)
        c.drawString(124*mm, 45*mm, 'fortgeschrittene Tricks')
        c.rect(123*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(123*mm, 21*mm, 31.5*mm, 23*mm)
        c.drawString(155.5*mm, 45*mm, 'schwierige Tricks')
        c.rect(154.5*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(154.5*mm, 21*mm, 31.5*mm, 23*mm)
        c.drawString(187*mm, 45*mm, 'sehr schwierige Tricks')
        c.rect(186*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(186*mm, 21*mm, 31.5*mm, 23*mm)
        c.drawString(218.5*mm, 45*mm, 'extrem schwierige Tricks')
        c.rect(217.5*mm, 44*mm, 31.5*mm, 4*mm)
        c.rect(217.5*mm, 21*mm, 31.5*mm, 23*mm)

        c.setFillColorRGB(0.88,0.94,0.85)
        c.setStrokeColorRGB(1,1,1)
        c.rect(60*mm, 14*mm, 157.5*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.setLineWidth(1)
        c.line(60*mm, 14*mm, 60*mm, 19*mm)
        c.line(217.5*mm, 14*mm, 217.5*mm, 19*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(61*mm, 15*mm, 'Sicherheit / Qualität')
        c.setFont('Helvetica', 7)
        c.drawString(61*mm, 11*mm, 'Stabilität und Kontrolle')
        c.rect(60*mm, 10*mm, 31.5*mm, 4*mm)
        c.rect(60*mm, 3*mm, 31.5*mm, 7*mm)
        c.drawString(91*mm, 11*mm, ' Körperhaltung, Gestig, Mimik')
        c.rect(91.5*mm, 10*mm, 31.5*mm, 4*mm)
        c.rect(91.5*mm, 3*mm, 31.5*mm, 7*mm)
        c.drawString(124*mm, 11*mm, 'Synchronisation auf Musik')
        c.rect(123*mm, 10*mm, 31.5*mm, 4*mm)
        c.rect(123*mm, 3*mm, 31.5*mm, 7*mm)
        c.drawString(155.5*mm, 11*mm, 'fließende Übergänge')
        c.rect(154.5*mm, 10*mm, 31.5*mm, 4*mm)
        c.rect(154.5*mm, 3*mm, 31.5*mm, 7*mm)
        c.drawString(187*mm, 11*mm, 'Geschwindigkeit und Dauer')
        c.rect(186*mm, 10*mm, 31.5*mm, 4*mm)
        c.rect(186*mm, 3*mm, 31.5*mm, 7*mm)

        c.setFillColorRGB(0.88,0.94,0.85)
        c.setStrokeColorRGB(1,1,1)
        c.rect(252.5*mm, 44*mm, 28*mm, 4*mm, fill=1)
        c.rect(252.5*mm, 29*mm, 28*mm, 4*mm, fill=1)
        c.rect(252.5*mm, 14*mm, 28*mm, 4*mm, fill=1)
        c.setFillColorRGB(0,0,0)
        c.setStrokeColorRGB(0.8,0,0)
        c.setLineWidth(2)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(253*mm, 45*mm, 'Anzahl')
        c.rect(253*mm, 34*mm, 27*mm, 10*mm)
        c.drawString(253*mm, 30*mm, 'Schwierigkeit')
        c.rect(253*mm, 19*mm, 27*mm, 10*mm)
        c.drawString(253*mm, 15*mm, 'Sicherheit / Qualität')
        c.rect(253*mm, 4*mm, 27*mm, 10*mm)
        c.setStrokeColorRGB(0,0,0)

    def printP(c):
        c.setFillColorRGB(0.87,0.92,0.97)
        c.setStrokeColorRGB(1,1,1)
        c.rect(60*mm, 48*mm, 72*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.line(60*mm, 48*mm, 60*mm, 53*mm)
        c.line(132*mm, 48*mm, 132*mm, 53*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(61*mm, 49*mm, 'Präsenz / Bewegungsausführung')
        c.rect(60*mm, 33*mm, 72*mm, 15*mm)
        c.rect(60*mm, 18*mm, 72*mm, 15*mm)
        c.drawString(90*mm, 4*mm, 'max. 10')
        c.setStrokeColorRGB(0.8,0,0)
        c.setLineWidth(2)
        c.rect(105*mm, 4*mm, 27*mm, 10*mm)
        c.setStrokeColorRGB(0,0,0)

        c.setFillColorRGB(0.87,0.92,0.97)
        c.setStrokeColorRGB(1,1,1)
        c.rect(134*mm, 48*mm, 72*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.setLineWidth(1)
        c.line(134*mm, 48*mm, 134*mm, 53*mm)
        c.line(206*mm, 48*mm, 206*mm, 53*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(135*mm, 49*mm, 'Komposition / Choreographie')
        c.rect(134*mm, 33*mm, 72*mm, 15*mm)
        c.rect(134*mm, 18*mm, 72*mm, 15*mm)
        c.drawString(164*mm, 4*mm, 'max. 10')
        c.setStrokeColorRGB(0.8,0,0)
        c.setLineWidth(2)
        c.rect(179*mm, 4*mm, 27*mm, 10*mm)
        c.setStrokeColorRGB(0,0,0)

        c.setFillColorRGB(0.87,0.92,0.97)
        c.setStrokeColorRGB(1,1,1)
        c.rect(208*mm, 48*mm, 72*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.setLineWidth(1)
        c.line(208*mm, 48*mm, 208*mm, 53*mm)
        c.line(280*mm, 48*mm, 280*mm, 53*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(209*mm, 49*mm, 'Interpretation der Musik / Timing')
        c.rect(208*mm, 33*mm, 72*mm, 15*mm)
        c.rect(208*mm, 18*mm, 72*mm, 15*mm)
        c.drawString(238*mm, 4*mm, 'max. 10')
        c.setStrokeColorRGB(0.8,0,0)
        c.setLineWidth(2)
        c.rect(253*mm, 4*mm, 27*mm, 10*mm)
        c.setStrokeColorRGB(0,0,0)

    def printD(c):
        c.setFillColorRGB(1,0.94,0.8)
        c.setStrokeColorRGB(1,1,1)
        c.rect(60*mm, 48*mm, 93*mm, 5.5*mm, fill=1)
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.line(60*mm, 48*mm, 60*mm, 53*mm)
        c.line(153*mm, 48*mm, 153*mm, 53*mm)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(61*mm, 49*mm, 'Abstiege')
        c.setFont('Helvetica', 8)
        c.rect(60*mm, 40*mm, 93*mm, 8*mm)
        c.drawString(61*mm, 42*mm, 'leicht (1 -2 Füße am Boden)')
        c.rect(60*mm, 26*mm, 93*mm, 14*mm)
        c.rect(60*mm, 18*mm, 93*mm, 8*mm)
        c.drawString(61*mm, 20*mm, 'schwer (Körper, Hand, Rad am Boden)')
        c.rect(60*mm, 4*mm, 93*mm, 14*mm)

        c.setLineWidth(2)
        c.setStrokeColorRGB(0.8,0,0)
        c.drawString(156*mm, 42*mm, 'Anzahl leichte Abstiege')
        c.rect(156*mm, 26*mm, 37*mm, 14*mm)
        c.drawString(156*mm, 20*mm, 'Anzahl schwere Abstiege')
        c.rect(156*mm, 4*mm, 37*mm, 14*mm)
        c.setStrokeColorRGB(0,0,0)

        c.setFont('Helvetica-Bold', 10)
        c.drawString(198*mm, 31*mm, 'x 0,5 =')
        c.drawString(198*mm, 9*mm, 'x 1,0 =')

        c.drawString(219*mm, 42*mm, '10 minus')
        c.rect(216*mm, 26*mm, 27*mm, 14*mm)
        c.rect(216*mm, 4*mm, 27*mm, 14*mm)

        c.drawString(246*mm, 9*mm, '=')
        c.rect(252*mm, 4*mm, 27*mm, 14*mm)
