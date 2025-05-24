# analysis/views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .eeg_processor import process_eeg_data
from .forms import EEGUploadForm
from .models import EEGData, EEGChannelAnalysis
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from scipy.interpolate import griddata
import numpy as np
from scipy.signal import butter, lfilter

def upload_eeg(request):
    if request.method == 'POST':
        form = EEGUploadForm(request.POST, request.FILES)
        if form.is_valid():
            eeg_data = form.save()
            process_eeg_data(eeg_data)
            return redirect('dashboard', eeg_id=eeg_data.id)
    else:
        form = EEGUploadForm()
    return render(request, 'upload.html', {'form': form})


def analyze_sentiment(analyses):
    # Cálculo das médias das potências
    avg = {
        'delta': np.mean([a.delta_power for a in analyses]),
        'theta': np.mean([a.theta_power for a in analyses]),
        'alpha': np.mean([a.alpha_power for a in analyses]),
        'beta': np.mean([a.beta_power for a in analyses]),
        'gamma': np.mean([a.gamma_power for a in analyses])
    }

    # Lógica de determinação de sentimentos
    sentiment = "Neutro"
    
    if avg['beta'] > avg['alpha'] * 1.5:
        sentiment = "Agitação/Estresse"
        if avg['gamma'] > 0.08: sentiment += " Intensa"
    elif avg['alpha'] > avg['beta'] * 1.2:
        sentiment = "Relaxamento"
        if avg['theta'] > 0.1: sentiment += " Profundo"
    elif avg['theta'] > avg['alpha'] and avg['theta'] > avg['beta']:
        sentiment = "Sonolência/Criatividade"
    
    return {
        'sentiment': sentiment,
        'avg_values': avg
    }

def create_brain_waves_plot(analyses):
    # Obter os dados do primeiro canal para exemplo (ou poderia calcular a média de todos os canais)
    first_channel = analyses[0]
    
    # Extrair os dados de tempo do sinal raw
    raw_data = json.loads(first_channel.raw_signal)
    timestamps = raw_data['x']
    
    # Criar gráfico de linhas para as bandas cerebrais
    fig = go.Figure()
    
    # Definir cores para cada banda
    colors = {
        'delta': 'rgba(220, 53, 69, 0.8)',  # Vermelho (Bootstrap danger)
        'theta': 'rgba(255, 193, 7, 0.8)',  # Amarelo (Bootstrap warning)
        'alpha': 'rgba(13, 202, 240, 0.8)',  # Azul claro (Bootstrap info)
        'beta': 'rgba(13, 110, 253, 0.8)',   # Azul (Bootstrap primary)
        'gamma': 'rgba(25, 135, 84, 0.8)'    # Verde (Bootstrap success)
    }
    
    # Processar os sinais para cada banda
    bandas = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 40)
    }
    
    # Obter os dados brutos do sinal
    raw_signal = np.array(raw_data['y'])
    
    # Calcular a média dos sinais de todos os canais para cada banda
    avg_signals = {}
    
    for banda, (low, high) in bandas.items():
        # Inicializar array para acumular sinais de todos os canais
        band_signals = np.zeros_like(raw_signal)
        
        # Para cada canal, extrair o sinal da banda e acumular
        for analysis in analyses:
            # Obter sinal bruto do canal
            channel_data = json.loads(analysis.raw_signal)
            channel_signal = np.array(channel_data['y'])
            
            # Aplicar filtro de banda
            fs = analysis.eeg_data.sampling_rate
            b, a = butter_bandpass(low, high, fs)
            filtered = lfilter(b, a, channel_signal)
            
            # Acumular o sinal filtrado
            band_signals += filtered
        
        # Calcular a média dos sinais de todos os canais
        avg_signals[banda] = band_signals / len(analyses)
    
    # Adicionar linhas para cada banda
    for banda, signal in avg_signals.items():
        # Normalizar o sinal para melhor visualização
        normalized_signal = signal / np.max(np.abs(signal)) * 0.5
        
        fig.add_trace(go.Scatter(
            x=timestamps[:500],  # Limitar para os primeiros 500 pontos para melhor visualização
            y=normalized_signal[:500],
            name=banda.capitalize(),
            line=dict(color=colors[banda], width=2)
        ))
    
    # Configurar layout
    fig.update_layout(
        title='Sinais das Ondas Cerebrais',
        xaxis_title='Tempo',
        yaxis_title='Amplitude (Normalizada)',
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig.to_html(full_html=False)

def dashboard(request, eeg_id):
    eeg_data = EEGData.objects.get(id=eeg_id)
    analyses = EEGChannelAnalysis.objects.filter(eeg_data=eeg_data)
    bandas = ['delta', 'theta', 'alpha', 'beta', 'gamma']
    
    # Gráfico de potências
    fig_power = px.line(title='Distribuição de Potência por Canal')
    for banda in bandas:
        values = [getattr(a, f'{banda}_power') for a in analyses]
        fig_power.add_scatter(
            x=[a.channel_name for a in analyses],
            y=values,
            name=banda.capitalize()
        )
    
    # Análise de sentimentos
    sentiment_analysis = analyze_sentiment(analyses)
    
    # Criar gráfico de ondas cerebrais
    brain_waves_plot = create_brain_waves_plot(analyses)
    
    return render(request, 'dashboard.html', {
        'eeg_data': eeg_data,
        'analyses': analyses,
        'bandas': [b.capitalize() for b in bandas],
        'power_plot': fig_power.to_html(full_html=False),
        'topomap_plot': get_topomap(analyses, 'Alpha'),
        'sentiment_analysis': sentiment_analysis,
        'brain_waves_plot': brain_waves_plot  # Novo gráfico de ondas cerebrais
    })

def get_topomap(analyses, banda):
    posicoes = {
        'EEG Channel 1': (0.5, 0.9),
        'EEG Channel 2': (0.3, 0.7),
        'EEG Channel 3': (0.7, 0.7),
        'EEG Channel 4': (0.2, 0.5),
        'EEG Channel 5': (0.8, 0.5),
        'EEG Channel 6': (0.5, 0.3),
        'EEG Channel 7': (0.3, 0.2),
        'EEG Channel 8': (0.7, 0.2)
    }

    valores = [getattr(a, f'{banda.lower()}_power') for a in analyses]
    x = np.array([posicoes[ch.channel_name][0] for ch in analyses])
    y = np.array([posicoes[ch.channel_name][1] for ch in analyses])
    z = np.array(valores)

    xi, yi = np.linspace(0, 1, 100), np.linspace(0, 1, 100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method='cubic')

    fig = px.imshow(
            zi,
            x=np.linspace(0, 1, 100),
            y=np.linspace(0, 1, 100),
            color_continuous_scale='Viridis',
            title=f'Mapa de Atividade {banda.capitalize()}'
        )
        
    return fig.to_html(
            full_html=False,
            include_plotlyjs=True,
            div_id='dynamic-topomap',  # ID único
            config={'responsive': True})
        
def update_topomap(request):
    eeg_id = request.GET.get('eeg_id')
    banda = request.GET.get('banda')
    analyses = EEGChannelAnalysis.objects.filter(eeg_data__id=eeg_id)
    
    # Retorne APENAS o HTML interno do gráfico (sem wrappers)
    return HttpResponse(
        get_topomap(analyses, banda)
    )


def channel_detail(request, channel_id):
    analysis = EEGChannelAnalysis.objects.get(id=channel_id)
    
    # Criar gráfico de filtros
    fig = make_subplots(
        rows=5, cols=1,
        subplot_titles=['Original', 'High-pass', 'Low-pass', 'Band-pass', 'Notch']
    )
    
    signals = {
        'Original': json.loads(analysis.raw_signal),
        'High-pass': json.loads(analysis.highpass),
        'Low-pass': json.loads(analysis.lowpass),
        'Band-pass': json.loads(analysis.bandpass),
        'Notch': json.loads(analysis.notch)
    }
    
    for i, (name, data) in enumerate(signals.items(), 1):
        fig.add_trace(
            go.Scatter(
                x=data['x'],
                y=data['y'],
                name=name,
                line=dict(width=1)
            ),
            row=i, col=1
        )
    
    fig.update_layout(height=1200, showlegend=False)
    fig.update_xaxes(title_text='Tempo Decorrido (s)')
    
    
    return render(request, 'channel_detail.html', {
        'analysis': analysis,
        'plot_div': fig.to_html(full_html=False)
    })


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
