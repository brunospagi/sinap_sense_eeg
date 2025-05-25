# EEG Analysis Platform 🧠

[![Django CI](https://github.com/brunospagi/sinap_sense_eeg/actions/workflows/django.yml/badge.svg)](https://github.com/brunospagi/sinap_sense_eeg/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete web-based solution for processing, visualizing, and interpreting EEG data with neurofeedback insights.

## 📑 Table of Contents
- [Key Features](#-key-features)
- [Technical Requirements](#-technical-requirements)
- [Installation](#-installation)
- [Data Format](#-data-format)
- [API Endpoints](#-api-endpoints)
- [Cognitive Detection Logic](#-cognitive-state-detection-logic)
- [Contributing](#-contributing)
- [License](#-license)

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
- **Patient Demographics**: Age/sex-based analysis customization
- **Batch Processing**: Support for multiple file uploads

## ⚙️ Technical Requirements
- Python 3.9+
- PostgreSQL (recommended) / SQLite
- 4GB RAM minimum
- Django 4.2+
- NumPy/SciPy/Pandas stack
- Plotly for visualization

## 🚀 Installation
```bash
# Clone repository
git clone https://github.com/brunospagi/sinap_sense_eeg.git
cd sinap_sense_eeg

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure database (PostgreSQL recommended)
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```
## 📊 Data Format
EEG data should be in CSV format with the following structure:
```bash
Timestamp,EEG Channel 1,EEG Channel 2,...,EEG Channel 8
1633024800000,12.45,-8.32,14.56,...,10.29
1633024801000,11.87,-7.91,13.78,...,9.64
```
Timestamp in milliseconds (will be auto-converted to seconds)

8 EEG channels minimum

Sampling rate: 250Hz recommended
## 📦 Dependency Stack (Verified Versions)

### Core Requirements (`requirements.txt`)
```python
# Framework & Utilities
Django==4.2.13           # Web framework
asgiref==3.8.1           # ASGI server
sqlparse==0.5.0          # SQL parsing

# Data Processing
numpy==1.26.4            # Numerical computing (CORRIGIDO: versão 2.2.6 é inválida)
pandas==2.2.3            # Data manipulation
scipy==1.13.0            # Signal processing (CORRIGIDO: versão 1.15.3 não existe)

# Visualization
plotly==6.1.1            # Interactive graphs
pillow==10.3.0           # Image processing

# Database
psycopg2-binary==2.9.9   # PostgreSQL adapter
dj-database-url==2.3.1   # DB URL parsing

# Security & Networking
certifi==2024.6.2        # SSL certificates
requests==2.32.3         # HTTP client

# Utilities
python-dateutil==2.9.0   # Date handling
pytz==2025.2             # Timezone support
```
## 🧠 Cognitive State Detection Logic
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
## 🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add some amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

Please report any issues using GitHub Issues.

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

## 📧 Contact
Bruno Gabriel - @brunospagi - bruno.gabriel@ufpr.br
