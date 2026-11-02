# SynapseCSV - AI Data Analyzer & Visualizer

A serverless-ready Python and Flask application that provides instant tabular data profiling, Matplotlib statistical visualizations, and Gemini AI executive reporting with an interactive natural language Q&A interface.

Designed from the ground up for **Vercel Serverless Deployment** and local execution.

---

## 🌟 Key Features

- **⚡ Stateless In-Memory CSV Engine**:
  - Automatically sniffs delimiters (`,` `;` `\t` `|`) and handles varied file encodings (`utf-8`, `latin-1`, `cp1252`).
  - Profiles column types (Numeric, Categorical, Datetime, Boolean, Text), missingness percentages, uniqueness, and value distributions.
  - Detects outliers using the Interquartile Range (IQR) method and calculates an overall **Data Health Score (0–100%)**.
  - Operates completely in-memory with strict 10 MB payload limits and zero dependence on persistent local filesystem storage.

- **📊 Serverless Matplotlib Visualizer**:
  - Uses the headless `Agg` backend with automatic figure cleanup to prevent memory leaks.
  - Renders custom distribution histograms with KDE curves, correlation heatmaps, categorical breakdown bar charts, and outlier boxplots.
  - Encodes graphics directly as Base64 PNGs for instantaneous frontend rendering.

- **🤖 Google Gemini AI Integration**:
  - Multi-model fallback pipeline supporting `gemini-flash-lite-latest`, `gemini-3.1-flash-lite`, and `gemini-3.8-flash`.
  - Generates structured executive summaries, key statistical patterns, data anomalies & risks, and strategic next steps.
  - **"Ask Your CSV" Interactive Q&A**: Users can query datasets in plain English with instant answers citing statistical metrics.

- **🎨 Modern Vector Art & Glassmorphism Dashboard**:
  - Custom SVG vector artwork for Logo, Hero Background, Upload state, Empty state, and animated Loading state.
  - Slate dark theme with vibrant cyan, electric blue, and violet gradients.
  - Fully responsive with drag-and-drop file upload, column explorer, and 25-row interactive data preview.

- **💾 Supabase Database & Auth**:
  - Persists analysis history, metadata summaries, and user chat queries.
  - Built-in user authentication (JWT-based signup, login, and guest mode).
  - Resilient local fallback engine ensuring smooth operation even if external database services are unreachable.

- **🚀 1-Click Built-in Sample Datasets**:
  - **E-Commerce Global Sales & Profit**: 25 orders tracking regional sales and margins.
  - **Customer Retention & Churn**: 20 subscriber records analyzing tenure and churn risk.
  - **Digital Marketing Campaign ROI**: 10 multi-channel campaigns comparing spend and conversions.

---

## 🏗️ Architecture & Project Structure

```
CSV Data Analyzer/
├── .env                  # Environment secrets (ignored in git)
├── .env.example          # Sample environment configuration
├── .gitignore            # Git exclusions
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel Serverless function routing
├── run.py                # Local server runner (http://localhost:5000)
├── api/
│   ├── __init__.py
│   └── index.py          # Vercel entry point (@vercel/python)
├── app/
│   ├── __init__.py       # Flask factory with CORS
│   ├── config.py         # Config & limits (10 MB upload cap)
│   ├── auth.py           # Password hashing & JWT verification
│   ├── analyzer.py       # In-memory CSV parsing & statistical engine
│   ├── visualizer.py     # Headless Matplotlib chart generator (Agg)
│   ├── gemini_service.py # Multi-model Gemini client & prompts
│   ├── supabase_service.py # Database persistence with offline fallback
│   ├── samples.py        # Preloaded CSV datasets
│   └── routes.py         # Flask Blueprint with REST API endpoints
├── static/
│   ├── css/style.css     # Glassmorphic dark theme stylesheet
│   ├── js/app.js         # Single page application client logic
│   └── img/              # Modern vector SVG assets
├── templates/
│   └── index.html        # Single page application dashboard
└── tests/                # Automated pytest suite
    ├── test_analyzer.py
    ├── test_visualizer.py
    └── test_api_endpoints.py
```

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+
- Pip

### 2. Environment Setup (Virtual Environment)
```bash
# Clone or navigate into the workspace
cd "CSV Data Analyzer"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (cmd):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Secrets
Copy `.env.example` to `.env` and provide your credentials:
```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-flash-lite-latest
GEMINI_MODELS=gemini-flash-lite-latest,gemini-3.1-flash-lite,gemini-3.8-flash

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret_key
PORT=5000
```

---

## 💻 Running the Application Locally

```bash
# Using the virtual environment
.\.venv\Scripts\python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🧪 Running Automated Tests

Run the full automated test suite verifying CSV parsing, statistical calculations, Matplotlib chart rendering, Gemini integration, and REST endpoints:

```bash
.\.venv\Scripts\python -m pytest tests -v
```

---

## ☁️ Deploying to Vercel

The application is pre-configured for Vercel using `api/index.py` and `vercel.json`.

1. Install the Vercel CLI or import the Git repository into the [Vercel Dashboard](https://vercel.com).
2. Set Environment Variables in your Vercel Project Settings:
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `JWT_SECRET`
3. Deploy! Vercel will automatically build the Python serverless function and route all traffic seamlessly to `api/index.py`.
