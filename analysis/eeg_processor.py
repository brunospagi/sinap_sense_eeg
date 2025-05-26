"""
    Processa e analisa dados de EEG de um arquivo associado ao objeto eeg_data.
    ...
"""

import pandas as pd
import numpy as np
import json
from scipy.signal import butter, lfilter, iirnotch, stft, filtfilt
from .models import EEGChannelAnalysis

def butter_highpass(cutoff, fs, order=4):
    """
    Projeta um filtro Butterworth passa-alta.
    
    Fórmulas:
        1. Frequência de Nyquist: f_nyq = 0.5 * fs
        2. Frequência normalizada: f_norm = cutoff / f_nyq
        3. Função de transferência (contínua): 
           |H(s)|² = 1 / (1 + (s/(2πf_c))^(2n))
        4. Transformação bilinear para domínio digital (z)
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_lowpass(cutoff, fs, order=4):
    """
    Projeta um filtro Butterworth passa-baixa.
    
    Fórmulas:
        1. Mesma normalização que o passa-alta
        2. Resposta em frequência:
           |H(f)| = 1 / sqrt(1 + (f/f_c)^(2n))
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order=4):
    """
    Projeta um filtro Butterworth passa-banda.
    
    Combinação de passa-alta (lowcut) e passa-baixa (highcut):
        H_bandpass(s) = H_highpass(s) * H_lowpass(s)
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def process_eeg_data(eeg_data):
    # Leitura e pré-processamento
    df = pd.read_csv(eeg_data.original_file.path)
    fs = eeg_data.sampling_rate
    
    # Ajuste do timestamp (Equação: t_sec = t_ms/1000)
    df['Timestamp'] = df['Timestamp'] / 1000
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
    
    for channel in df.columns[1:9]:
        data = df[channel].values
        
        # Aplicação de filtros com comentários matemáticos
        # --------------------------------------------------
        # Filtro Notch para 60 Hz (Rejeição de banda estreita)
        # Função de transferência: H(s) = (s² + ω₀²)/(s² + (ω₀/Q)s + ω₀²)
        # Onde: ω₀ = 2π*60, Q = 30
        b, a = iirnotch(60, 30, fs)
        notch = filtfilt(b, a, data)
        
        # Cadeia de filtros Butterworth (aplicação sequencial)
        # Highpass: Remove componentes < 0.5 Hz
        b, a = butter_highpass(0.5, fs)
        filtered = filtfilt(b, a, notch)
        
        # Lowpass: Remove componentes > 40 Hz
        b, a = butter_lowpass(40, fs)
        filtered = filtfilt(b, a, filtered)
        
        # Bandpass: Isola 1-30 Hz (combinação highpass + lowpass)
        b, a = butter_bandpass(1, 30, fs)
        bandpass = filtfilt(b, a, filtered)
        
        # Cálculo do Espectrograma (STFT)
        # Equação: X(τ,ω) = ∫ x(t)w(t-τ)e^(-jωt) dt
        # Implementação discreta: janelas de 256 amostras
        f, t, Zxx = stft(bandpass, fs=fs, nperseg=256)
        
        # Cálculo de Potência em Bandas
        # Energia = Média do quadrado do sinal (P = 1/N Σ x[n]²)
        bandas = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 40)
        }
        
        power_metrics = {}
        for banda, (low, high) in bandas.items():
            b, a = butter_bandpass(low, high, fs)
            filtered_band = filtfilt(b, a, bandpass)
            power_metrics[f'{banda}_power'] = np.mean(filtered_band**2)
        
        # Armazenamento com dados serializados
        EEGChannelAnalysis.objects.create(
            eeg_data=eeg_data,
            channel_name=channel,
            raw_signal=json.dumps({'x': df['Timestamp'].tolist(), 'y': data.tolist()}),
            notch_filtered=json.dumps({'x': df['Timestamp'].tolist(), 'y': notch.tolist()}),
            bandpass_filtered=json.dumps({'x': df['Timestamp'].tolist(), 'y': bandpass.tolist()}),
            spectrogram_data=json.dumps({
                'freq': f.tolist(),
                'time': t.tolist(),
                'magnitude': np.abs(Zxx).tolist()
            }),
            **power_metrics
        )
    
    eeg_data.processed = True
    eeg_data.save()