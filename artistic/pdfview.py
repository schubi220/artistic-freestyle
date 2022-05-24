from django.conf import settings
from reportlab.lib.pagesizes import A3, landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import math
import datetime

def pdfdetail(context):
    c = SimpleDocTemplate(str(settings.BASE_DIR) + '/tmp/pdfdetail.pdf', pagesize=landscape(A3), rightMargin=56, leftMargin=56, topMargin=56, bottomMargin=56)
    pagecontext = []
    sample_style_sheet = getSampleStyleSheet()
    sample_style_sheet['Heading1'].spaceBefore = 25

    for jtype in context['judgetypes']:
        pagecontext.append(Paragraph(jtype, sample_style_sheet['Heading1']))
        data =[]
        #row = ['#', 'Name', 'Verein', 'Titel', 'Gesamt']
        row = ['#', 'Name', 'Verein']
        row.append(jtype)
        for judge in context['judges']:
            if judge.type == jtype:
                row.append(judge.possition)
                row.append('')
                #row.append('')
                row.append('1')
                row.append('2')
                row.append('3')
        data.append(row)

        for start in context['starts']:
            row = []
            row.append(start.order)
            row.append(start.competitors_names()[0:32])
            row.append(start.competitors_clubs()[0:18])
            #row.append(start.info)
#            row.append(f"{context['result']['full'][start.id] * 100.0:.{2}f}%")
            row.append(f"{context['result'][jtype][start.id] * 100.0:.{2}f}%")
            for judge in context['judges']:
                if judge.type == jtype:
                    row.append(context['values'][judge.possition][start.id].values['place'])
                    row.append(f"{context['values'][judge.possition][start.id].values['result'] * 100.0:.{2}f}%")
                    #row.append(context['values'][judge.possition][start.id].values['summe'])
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
    pagecontext.append(Paragraph("Gesamt", sample_style_sheet['Heading1']))
    data =[]
    #row = ['#', 'Name', 'Verein', 'Titel', 'Gesamt']
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
        #row.append(start.info)
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

    c.build(pagecontext)
    #c.multiBuild(pagecontext, canvasmaker=FooterDetail)

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
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont("Helvetica", 6)
        self.drawString(20, 25, 'Altersklasse: ')
        self.drawCentredString(575.2755905511812, 25, "Seite %s von %s" % (self._pageNumber, page_count))
        self.drawRightString(1150.551181102, 25, 'Ergebnis vom: '+datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        self.restoreState()

def pdfresult(context):
    c = SimpleDocTemplate(str(settings.BASE_DIR) + '/tmp/pdfresult.pdf', pagesize=A4, rightMargin=56, leftMargin=56, topMargin=56, bottomMargin=56)
    pagecontext = []
    sample_style_sheet = getSampleStyleSheet()
    data =[]

    sample_style_sheet['Heading1'].alignment = 1
    pagecontext.append(Paragraph('Bayerische Meisterschaft 2022', sample_style_sheet['Heading1']))
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
        row.append(Paragraph(start.info, sample_style_sheet['Normal']))
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
        self.line(0, 420.94488189, 20, 420.94488189)
        self.setStrokeColorRGB(0, 0, 0)
        self.setFont("Helvetica", 6)
        self.drawString(20, 25, "Seite %s von %s" % (self._pageNumber, page_count))
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

    w, h = A4
    for cnt in context['result']['place']:
        start = context['starts'][cnt]
        c.drawCentredString(297.637795276,700, str(context['result']['place'][cnt]) + '. Platz')
        c.drawCentredString(297.637795276,650, f"{context['result']['full'][start.id] * 100.0:.{2}f}%")
        c.drawCentredString(297.637795276,600, start.competitors_names())
        c.drawCentredString(297.637795276,550, start.competitors_clubs())
        c.drawCentredString(297.637795276,500, start.info)
        c.showPage()

    c.save()

