# EEG Analysis Platform 🧠

A complete web-based solution for processing, visualizing, and interpreting EEG data with neurofeedback insights.

## 🌟 Key Features
- **Multi-Channel Processing**: Supports 8 EEG channels with customizable electrode positions
- **Advanced Filtering Suite**
  - High-pass (0.5Hz)
  - Low-pass (40Hz)
  - Notch filter (60Hz)
  - Customizable bandpass ranges
- **Quantitative EEG Analysis**
  - Delta (0.5-4Hz)
  - Theta (4-8Hz)
  - Alpha (8-13Hz)
  - Beta (13-30Hz)
  - Gamma (30-40Hz)
- **Neurocognitive State Detection**: Real-time emotional/cognitive state estimation
- **Interactive 3D Topomaps**: Dynamic brain activity visualization
- **Signal Comparison**: Side-by-side raw vs filtered signal viewing

## ⚙️ Technical Requirements
- Python 3.9+
- PostgreSQL (recommended) / SQLite
- 4GB RAM minimum
- CSV input format:
  ```csv
  Timestamp,EEG Channel 1,EEG Channel 2,...,EEG Channel 8
  1633024800000,12.45,-8.32,14.56,...,10.29
# Clone repository
git clone https://github.com/brunospagi/sinap_sense_eeg.git
cd eeg-analysis-platform

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure database
python manage.py makemigrations
python manage.py migrate

# Run development server
python manage.py runserver

# 🧠 Cognitive State Detection Logic
```
def detect_mental_state(alpha, beta, theta, gamma):
    if beta > 1.5*alpha:
        return "High Cognitive Load 🧠🔥"
    elif alpha > 1.2*beta:
        return "Relaxed State 😌"
    elif theta > max(alpha, beta):
        return "Creative Flow 🎨"
    else:
        return "Neutral State ⚖️"
```

