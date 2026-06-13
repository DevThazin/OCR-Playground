# 🔍 OCR Playground – Multilingual OCR Comparison Platform

A research-oriented OCR application that compares multiple OCR engines on the same image, 
with interactive visualisation, confidence scoring, runtime benchmarking, and downloadable results.

Built as a PhD/research portfolio project.

---

## Features

- **Multi-engine OCR** – EasyOCR & Tesseract OCR run simultaneously on the same image
- **Bounding box visualisation** – Per-word detection boxes drawn on the original image
- **Confidence analysis** – Average, min, max confidence with distribution charts
- **Runtime benchmarking** – Wall-clock comparison across engines
- **15 languages** – English, Burmese, Hindi, Bengali, Tamil, Telugu, Kannada, Malayalam, Thai, Chinese (Simplified & Traditional), Japanese, Korean, Arabic, Russian
- **Auto-detect mode** – Multilingual EasyOCR detection
- **Downloadable results** – Export OCR text and CSV reports
- **Extensible architecture** – PaddleOCR, TrOCR, DocTR slots ready

---

## Project Structure

```
OCR-Playground/
│
├── app.py                        # Streamlit main application (Phase 3)
├── requirements.txt              # Python dependencies
├── packages.txt                  # System dependencies (Tesseract) for Streamlit Cloud
├── README.md
│
├── OCR_Playground_Colab.ipynb    # ← Phase 2: run this in Google Colab
│
├── config/
│   ├── __init__.py
│   └── languages.py              # All 15 language mappings (single source of truth)
│
├── ocr_engines/
│   ├── __init__.py
│   ├── easyocr_engine.py         # EasyOCR wrapper
│   └── tesseract_engine.py       # Tesseract wrapper
│
├── utils/
│   ├── __init__.py
│   ├── image_utils.py            # Loading, validation, preprocessing
│   ├── visualization.py          # Bounding-box drawing, comparison panels
│   ├── benchmarking.py           # Runtime measurement, summary tables
│   └── metrics.py                # Confidence stats, CER/WER
│
├── assets/                       # Static assets (logos, CSS)
├── sample_images/                # Example images for testing
└── results/                      # Output files (gitignored)
```

---

## Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR binary

### Tesseract Installation

**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Then add to PATH. Also set in pytesseract:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-all
```

**Verify:**
```bash
tesseract --version
```

### Python Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/OCR-Playground.git
cd OCR-Playground

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Running Locally

### Google Colab Prototype
Open `OCR_Playground_Colab.ipynb` in Google Colab and run all cells.

### Streamlit Application
```bash
streamlit run app.py
```
Then open `http://localhost:8501` in your browser.

---

## Deployment (Streamlit Community Cloud)

1. Push your project to a public GitHub repository (see Git Commands below)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repo → set **Main file path** to `app.py`
4. Click **Deploy**

Streamlit Cloud reads `packages.txt` automatically to install Tesseract.

---

## Git Commands

```bash
# Initialise the repository
git init

# Stage all files
git add .

# Create the first commit
git commit -m "Initial commit – OCR Playground Phase 1 & 2"

# Link to your GitHub remote (replace URL)
git remote add origin https://github.com/YOUR_USERNAME/OCR-Playground.git

# Push to GitHub
git push -u origin main
```

---

## Supported Languages

| Language            | EasyOCR | Tesseract |
|---------------------|---------|-----------|
| English             | en      | eng       |
| Burmese (Myanmar)   | my      | mya       |
| Hindi               | hi      | hin       |
| Bengali             | bn      | ben       |
| Tamil               | ta      | tam       |
| Telugu              | te      | tel       |
| Kannada             | kn      | kan       |
| Malayalam           | ml      | mal       |
| Thai                | th      | tha       |
| Chinese Simplified  | ch_sim  | chi_sim   |
| Chinese Traditional | ch_tra  | chi_tra   |
| Japanese            | ja      | jpn       |
| Korean              | ko      | kor       |
| Arabic              | ar      | ara       |
| Russian             | ru      | rus       |

---

## Screenshots

*Coming soon – add screenshots of the Streamlit app here after Phase 3.*

---

## Future Improvements (Phase 5)

1. PaddleOCR integration
2. TrOCR (Transformer-based) integration
3. CER / WER calculation against ground truth
4. PDF OCR support
5. Batch image processing
6. OCR accuracy leaderboard
7. Error heatmaps
8. Historical document OCR mode
9. JSON / Excel export
10. Document layout analysis
11. OCR attention visualisation
12. Language detection improvements

---

## Accounts Required

| Service | Purpose | Link |
|---------|---------|------|
| GitHub | Host source code for deployment | [github.com](https://github.com) |
| Streamlit Community Cloud | Free app hosting | [share.streamlit.io](https://share.streamlit.io) |

---

## Tech Stack

- **Python 3.10+**
- **EasyOCR** – Deep-learning OCR (CRNN + CRAFT)
- **Tesseract OCR** – Classical OCR engine
- **Streamlit** – Web application framework
- **OpenCV** – Image processing
- **Pillow** – Image I/O
- **Pandas** – Data export
- **Matplotlib** – Visualisations
