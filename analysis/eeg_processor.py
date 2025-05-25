"""
    Processa e analisa dados de EEG de um arquivo associado ao objeto eeg_data.
    Este método realiza as seguintes etapas para cada canal de EEG:
    1. Lê os dados brutos do arquivo CSV associado.
    2. Ajusta o timestamp para o formato datetime apropriado.
    3. Aplica filtros digitais (highpass, lowpass, bandpass, notch) ao sinal.
    4. Calcula o espectrograma do sinal usando STFT.
    5. Calcula a potência média em diferentes bandas de frequência (delta, theta, alpha, beta, gamma).
    6. Salva os resultados processados e métricas em registros do modelo EEGChannelAnalysis.
    7. Atualiza o status do objeto eeg_data para indicar que o processamento foi concluído.
    Parâmetros:
        eeg_data (EEGData): Instância contendo informações do arquivo de EEG e metadados necessários para o processamento.
    Observações:
        - Requer que as funções de filtro digital (butter_highpass, butter_lowpass, butter_bandpass, iirnotch) estejam implementadas.
        - Utiliza pandas, numpy, scipy.signal e json para manipulação e análise dos dados.
        - Os resultados são salvos no banco de dados via o modelo EEGChannelAnalysis.
    """
import pandas as pd
import numpy as np
import json
from scipy.signal import butter, lfilter, iirnotch , stft
from .models import EEGChannelAnalysis


def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_lowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def process_eeg_data(eeg_data):
    df = pd.read_csv(eeg_data.original_file.path)
    fs = eeg_data.sampling_rate
    
    # Ajustar o timestamp para o formato correto
    df['Timestamp'] = df['Timestamp'] / 1000  # Converter de milissegundos para segundos
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
    df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    for channel in df.columns[1:9]:
        data = df[channel].values
        timestamp = df['Timestamp'].values
        
        # Aplicar filtros
        b, a = butter_highpass(0.5, fs)
        highpass = lfilter(b, a, data)
        
        b, a = butter_lowpass(40, fs)
        lowpass = lfilter(b, a, data)
        
        b, a = butter_bandpass(1, 30, fs)
        bandpass = lfilter(b, a, data)
        
        b, a = iirnotch(60, 30, fs)
        notch = lfilter(b, a, data)
        
        # Calcular potências
        bandas = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 40)
        }

        # Calcula o espectrograma
        f,t, Zxx = stft(data, fs=fs, nperseg=256)
            
            # Normaliza e prepara os dados
        spectrogram = {
                'freq': f.tolist(),
                'time': t.tolist(),
                'magnitude': np.abs(Zxx).tolist(),
                'config': {
                    'fmin': 0,
                    'fmax': 40,
                    'cmap': 'Viridis'
                }
            }
        
        power_metrics = {}
        for banda, (low, high) in bandas.items():
            b, a = butter_bandpass(low, high, fs)
            filtered = lfilter(b, a, data)
            power_metrics[f'{banda}_power'] = np.mean(filtered**2)
        
        # Criar registro
        EEGChannelAnalysis.objects.create(
            eeg_data=eeg_data,
            channel_name=channel,
            raw_signal=json.dumps({'x': timestamp.tolist(), 'y': data.tolist()}),
            highpass=json.dumps({'x': timestamp.tolist(), 'y': highpass.tolist()}),
            lowpass=json.dumps({'x': timestamp.tolist(), 'y': lowpass.tolist()}),
            bandpass=json.dumps({'x': timestamp.tolist(), 'y': bandpass.tolist()}),
            notch=json.dumps({'x': timestamp.tolist(), 'y': notch.tolist()}),
            spectrogram_data=json.dumps(spectrogram),
            **power_metrics
        )
    
    eeg_data.processed = True
    eeg_data.save()