"""Real PDF, with vector ECG drawing. No browser, model or external service."""
from io import BytesIO
from xml.sax.saxutils import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, PolyLine, Line, String, Circle
from app_theme import PDF_PALETTE


def ecg_drawing(plot, unit):
    drawing = Drawing(440,205)
    t,raw,filtered = plot['time'],plot['raw'],plot['filtered']
    lo,hi = min(min(raw),min(filtered)),max(max(raw),max(filtered))
    span = max(hi-lo,1e-9)
    x = lambda v: 40+385*(v-t[0])/max(t[-1]-t[0],.001)
    y = lambda v: 38+130*(v-lo)/span
    for coords in [(40,38,425,38),(40,38,40,168)]:
        drawing.add(Line(*coords,strokeColor=colors.HexColor(PDF_PALETTE['axis'])))
    for values,color in [(raw,PDF_PALETTE['raw']),(filtered,PDF_PALETTE['filtered'])]:
        points = [c for tx,amplitude in zip(t,values) for c in (x(tx),y(amplitude))]
        drawing.add(PolyLine(points,strokeColor=colors.HexColor(color),strokeWidth=.45))
    for tx,amplitude in zip(plot['r_time'],plot['r_amp']):
        drawing.add(Circle(x(tx),y(amplitude),2,fillColor=colors.HexColor(PDF_PALETTE['marker']),strokeWidth=0))
    drawing.add(String(40,183,'Original | Filtrado | Candidatos R (sin verificar)',fontSize=9))
    drawing.add(String(40,20,f'{t[0]:.3f} s',fontSize=8))
    drawing.add(String(375,20,f'{t[-1]:.3f} s',fontSize=8))
    drawing.add(String(0,165,f'{hi:.2f}',fontSize=8))
    drawing.add(String(0,38,f'{lo:.2f}',fontSize=8))
    drawing.add(String(40,3,f'Tiempo desde inicio del archivo (s); amplitud en {unit}',fontSize=8))
    return drawing


def build_pdf(evaluation):
    out = BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(out,title="IMPULSO | Evaluación ECG",author="IMPULSO",pagesize=(21*cm,29.7*cm))
    story: list = []
    def text(value, style="BodyText"):
        story.append(Paragraph(escape(str(value)),styles[style]))
        story.append(Spacer(1,6))
    text("IMPULSO | Resultados ECG", "Title")
    if evaluation["synthetic"]:
        text("DEMOSTRACIÓN: identidad y señal ficticias. No es un registro de paciente.")
    elif evaluation.get('identity_fictitious'):
        text("Identidad de demostración. ECG procedente de un archivo subido; no se identifica como señal sintética.")
    person, report = evaluation["person"], evaluation["report"]
    text(f"Persona evaluada: {person['first_name']} {person['last_name']} | Edad: {person['age']} años")
    text(f"Evaluación: {evaluation['evaluation_id']}")
    date = datetime.fromisoformat(evaluation["created"]).astimezone(ZoneInfo("America/Lima"))
    text(f"Fecha de evaluación: {date:%d/%m/%Y %H:%M:%S} (America/Lima)")
    text(f"Operador responsable: {evaluation['operator']['display']} (identidad diferente de la persona evaluada)")
    acquisition, params = report["acquisition"], report["parameters"]
    text(f"Fuente: {acquisition['source']} | canal: {acquisition['channel'] or 'único'} | "
         f"fs: {acquisition['sampling_rate_hz']:g} Hz | amplitud: {acquisition['unit']}")
    full = report.get('analysis_scope','segment') == 'full_record'
    text('Análisis del registro completo' if full else 'Análisis histórico de un segmento (no es un análisis completo)', 'Heading2')
    text(f"Alcance: inicio {acquisition['start_s']:g} s, duración analizada {acquisition['duration_s']:g} s; "
         f"archivo de {acquisition['file_duration_s']:g} s; {acquisition['samples']} muestras analizadas.")
    text(f"Filtro: 0.5–40 Hz, Butterworth orden 4, fase cero; notch solicitado {params['mains_hz']} Hz "
         f"(0 = desactivado); inversión: {params['invert']}; BPM máximo detector: {params['max_bpm']}.")
    text("Mediciones globales del registro" if full else "Mediciones del segmento", "Heading2")
    labels = {"bpm":"FC estimada (BPM)","n_peaks":"Picos automáticos", "n_rr":"Intervalos RR",
              "mean_rr_ms":"Media RR (ms)","sdnn_rr_ms":"SD de RR, ddof=0 (ms)"}
    rows = [[label,"No disponible" if report['metrics'][key] is None else f"{report['metrics'][key]:.2f}"] for key,label in labels.items()]
    table = Table(rows,colWidths=[10*cm,5*cm],hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor(PDF_PALETTE['table'])),
                               ("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story.append(table)
    if evaluation.get('overview'):
        text("Vista global del registro analizado", "Heading2")
        story.append(ecg_drawing(evaluation['overview'],acquisition['unit']))
    text("Detalle: primeros hasta 10 s (solo ilustracion)", "Heading2")
    story.append(ecg_drawing(evaluation['plot'],acquisition['unit']))
    text(f"Algoritmo: {report['detector']}. Los marcadores no son anotaciones manuales.")
    text(f"Regla RR preliminar: desviación > {params['rr_deviation']:.0%} respecto a la media global; "
         f"{report['rr_rule']['outside_threshold_count']} intervalos fuera del umbral. No es clasificación N/S/V/F.")
    text("AAMI: no disponible. Bigeminismo, trigeminismo, parejas y rachas: no evaluados.")
    text("Limitaciones del prototipo experimental", "Heading2")
    for caution in report['cautions']:
        text(caution)
    text("La gráfica usa reducción solo visual. Las mediciones usan todas las muestras del registro completo." if full else
         "La gráfica usa reducción solo visual. Las mediciones históricas corresponden al segmento guardado.")
    text(f"Huella SHA-256 del archivo: {report['source_sha256']}")
    text("Este reporte no contiene un diagnóstico y no sustituye la revisión profesional, el triaje ni el ECG diagnóstico de 12 derivaciones.")
    def footer(canvas, _doc):
        canvas.setFont("Helvetica",8)
        canvas.drawString(40,25,f"IMPULSO · Prototipo experimental · Página {canvas.getPageNumber()}")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
