# StyleSense 🎨✦
### Generative AI-Powered Fashion Recommendation System

StyleSense analyzes your photo using computer vision to detect your skin tone, then generates a complete personalized style profile including outfit recommendations, hairstyle advice, accessories, and direct shopping links — powered by 4 AI providers.

---

## 🤖 AI Stack

| Provider | Role |
|---|---|
| **Gemini** (Google) | Image vision — skin tone detection from photo |
| **Groq** (LLaMA) | Primary text generation — fast outfit/style recommendations |
| **IBM watsonx** (Granite) | Secondary text generation — enterprise-grade AI fallback |
| **Hugging Face** | Style vibe classification + tertiary text generation |

> All providers work independently. The system cascades: Groq → IBM → Hugging Face → Gemini → Demo Mode

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (optional — app works in demo mode without keys)

Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

| Key | Where to Get |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) — Free |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — Free |
| `HF_API_TOKEN` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — Free |
| `IBM_API_KEY` + `IBM_PROJECT_ID` | [ibm.com/watsonx](https://www.ibm.com/watsonx) — Free tier |

### 3. Run the server
```bash
python main.py
```

Open **http://localhost:8000** in your browser.

---

## 📂 Project Structure

```
stylesense/
├── main.py              # FastAPI app entry point
├── requirements.txt     
├── .env                 # Your API keys (not committed)
├── .env.example         # Template
├── routes/
│   ├── analyze.py       # POST /api/analyze — core AI pipeline
│   ├── recommend.py     # POST /api/recommend — text-based recommendations
│   ├── trends.py        # GET  /api/trends — fashion trend report
│   └── stylist.py       # POST /api/stylist — AI chat stylist
├── utils/
│   ├── gemini_client.py # Google Gemini SDK wrapper
│   ├── groq_client.py   # Groq SDK wrapper
│   ├── hf_client.py     # Hugging Face Inference API client
│   └── ibm_client.py    # IBM watsonx REST API client
└── frontend/
    ├── index.html       # Single-page app
    ├── style.css        # Dark theme, glassmorphism styling
    └── app.js           # Upload, analysis, results rendering
```

---

## 🎯 Features

- **📸 Photo-based skin tone analysis** — Gemini Vision detects tone, hex, RGB, undertone
- **👔 Complete outfit recommendations** — specific brands, colors, fabrics
- **💇 Hairstyle advice** — personalized with step-by-step how-to
- **💎 Accessories guide** — 4 curated accessories per profile
- **🎨 Color palette** — primary / secondary / accent with visual swatches
- **🛍️ Shop Your Style** — direct Amazon.in links for each recommended item
- **🔥 Fashion trends** — current season trend report
- **💬 AI Stylist chat** — interactive fashion Q&A
- **🔒 Demo Mode** — full UI preview without any API keys

---

## 🛠️ Tech Stack

`FastAPI` · `HTML5` · `CSS3` · `Vanilla JavaScript` · `Google Gemini AI` · `Groq (LLaMA)` · `IBM Granite (watsonx)` · `Hugging Face`
