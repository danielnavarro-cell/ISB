"""Interactive presentation only: never send reduced samples to processing."""
import numpy as np
import plotly.graph_objects as go

from p4_pipeline import AnalysisResult, display_indices
from app_theme import PALETTE, CHART_TEMPLATE


def ecg_figure(result: AnalysisResult, start_s: float, end_s: float) -> go.Figure:
    indices = display_indices(result, start_s, end_s)
    origin = result.acquisition["start_s"]
    time = origin + indices / result.fs
    peaks = result.peaks[(origin + result.peaks/result.fs >= start_s)
                         & (origin + result.peaks/result.fs <= end_s)]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=time, y=result.raw[indices], name="ECG original",
                              mode="lines", line=dict(color=PALETTE['raw'], width=1),
                              hovertemplate="%{x:.3f} s · %{y:.2f}<extra>Original</extra>"))
    filtered_name = "Filtrado · polaridad invertida" if result.config.invert else "ECG filtrado"
    fig.add_trace(go.Scattergl(x=time, y=result.filtered[indices], name=filtered_name,
                              mode="lines", line=dict(color=PALETTE['accent'], width=1.4),
                              hovertemplate="%{x:.3f} s · %{y:.2f}<extra>Filtrado</extra>"))
    fig.add_trace(go.Scattergl(x=origin+peaks/result.fs, y=result.filtered[peaks],
                              mode="markers", name="Picos R detectados (sin verificar)",
                              marker=dict(color=PALETTE['marker'], size=8, symbol="diamond"),
                              hovertemplate="%{x:.3f} s<extra>Pico detectado</extra>"))
    fig.update_layout(height=440, margin=dict(l=12, r=12, t=15, b=30),
                      template=CHART_TEMPLATE, paper_bgcolor=PALETTE['panel'], plot_bgcolor=PALETTE['panel'],
                      dragmode="pan", legend=dict(orientation="h", y=1.17, x=0),
                      xaxis=dict(title="Tiempo desde el inicio del archivo (s)",
                                 range=[start_s, end_s], rangeslider=dict(visible=True, thickness=.10)),
                      yaxis=dict(title=f"Amplitud ({result.acquisition['unit']})", fixedrange=False))
    return fig


def rr_figure(result: AnalysisResult) -> go.Figure:
    table = result.rr_table
    fig = go.Figure(go.Scatter(x=table.fin_s, y=table.rr_ms, mode="lines+markers",
                              name="RR detectado", line=dict(color=PALETTE['accent']),
                              marker=dict(color=np.where(table.regla_rr == "Fuera del umbral RR",
                                                         PALETTE['marker'], PALETTE['accent'])),
                              hovertemplate="%{x:.3f} s · %{y:.1f} ms<extra>RR</extra>"))
    mean = result.metrics["mean_rr_ms"]
    if mean is not None:
        fig.add_hline(y=mean, line_dash="dash", line_color=PALETTE['raw'], annotation_text="Media RR")
        for sign in (-1, 1):
            fig.add_hline(y=mean*(1+sign*result.config.rr_deviation), line_dash="dot",
                          line_color=PALETTE['marker'])
    fig.update_layout(height=320, template=CHART_TEMPLATE, paper_bgcolor=PALETTE['panel'],
                      plot_bgcolor=PALETTE['panel'], margin=dict(l=12, r=12, t=25, b=25),
                      xaxis_title="Final del intervalo desde inicio del archivo (s)",
                      yaxis_title="Intervalo RR (ms)")
    return fig


def plot_snapshot(result, start_s, end_s, max_points=2500):
    """Reduced drawing only. Both metrics and R indices remain full resolution."""
    origin = result.acquisition['start_s']
    indices = display_indices(result,start_s,end_s,max_points=max_points)
    times = origin+result.peaks/result.fs
    peaks = result.peaks[(times>=start_s)&(times<=end_s)]
    return dict(time=(origin+indices/result.fs).tolist(),raw=result.raw[indices].tolist(),
                filtered=result.filtered[indices].tolist(),r_time=(origin+peaks/result.fs).tolist(),
                r_amp=result.filtered[peaks].tolist())


def snapshot_figure(plot, unit):
    fig = go.Figure()
    for name,key,color in [('Original','raw',PALETTE['raw']),('Filtrado','filtered',PALETTE['accent'])]:
        fig.add_trace(go.Scattergl(x=plot['time'],y=plot[key],mode='lines',name=name,line=dict(color=color)))
    fig.add_trace(go.Scattergl(x=plot['r_time'],y=plot['r_amp'],mode='markers',name='Candidatos R',marker_color=PALETTE['marker']))
    fig.update_layout(template=CHART_TEMPLATE,height=330,xaxis_title='Tiempo desde inicio del archivo (s)',
                      yaxis_title=unit,legend_orientation='h',paper_bgcolor=PALETTE['panel'],plot_bgcolor=PALETTE['panel'])
    return fig
