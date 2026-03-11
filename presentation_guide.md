# 🎨 StyleSense – Presentation & Architecture Guide

This guide is designed to help you explain the **StyleSense: Generative AI-Powered Fashion Recommendation System** to an audience or jury. It breaks down the project structure, the flow of data, and how the AI models work together.

---

## 🏗️ 1. High-Level Project Overview
**What is StyleSense?**
StyleSense is a web application that acts as a personal AI fashion stylist. Users upload a photo of themselves, and the system uses Computer Vision and Large Language Models (LLMs) to analyze their skin tone, suggest color palettes, build full outfits, and provide shopping links.

**Why is it special?**
Instead of relying on basic "if-then" rules or a static database of clothes, StyleSense uses **Generative AI** to dynamically create personalized advice on the fly. It utilizes a powerful "AI Cascade" fallback system to ensure it's always fast and reliable, offering both photo-based and text-based style consultations.

---

## 📂 2. Project Structure Explained
Here is how the codebase is organized and what each part does:

### 🖥️ The Backend (FastAPI - Python)
*   **`main.py`**: The heart of the application. It boots up the server, sets up security (CORS), connects all the different API routes, and serves the frontend files to the browser.
*   **`routes/`**: This folder contains the "endpoints" (the URLs the frontend talks to).
    *   **`analyze.py`**: The core logic for photo analysis. This handles the photo upload, talks to the AI models to detect skin tone, and generates the final outfit JSON.
    *   **`recommend.py`**: Handles the "Text Styling" feature, taking manual user preferences (body type, occasion, budget) and returning tailored outfits.
    *   **`trends.py`**: Fetches the latest seasonal fashion trends.
    *   **`stylist.py`**: Powers the interactive AI chatbot.
*   **`utils/`**: This folder contains the "clients" that actually communicate with the external AI providers (Google, Groq, IBM, Hugging Face). It keeps the code clean by hiding the complex API connection logic.

### 🎨 The Frontend (HTML/CSS/JS)
*   **`index.html`**: The single page that the user sees. It contains the layout, the hero section, the upload dropzone, and the hidden result cards.
*   **`style.css`**: Provides the modern, premium "glassmorphism" design, dark theme, and smooth animations.
*   **`app.js`**: The brain of the browser. It handles dragging and dropping the photo, showing the loading spinner, sending the photo to the backend (`/api/analyze`), and dynamically injecting the AI's response into the HTML cards.

---

## 🧠 3. Step-by-Step Logic Flow (How it Works)
When you are presenting, walk the jury through the exact flow of what happens when a user requests style advice. The app offers two paths:

### Path A: "Photo Analysis" Flow

#### Step 1: The User Uploads a Photo
1.  The user drags a photo into the browser and selects their gender.
2.  `app.js` packages the photo and gender into a `FormData` object and securely sends an HTTP POST request to the backend backend at `/api/analyze`.

#### Step 2: Computer Vision (Gemini)
1.  The backend receives the photo in `analyze.py`.
2.  It sends the image bytes directly to **Google Gemini 1.5 Flash** (via `utils/gemini_client.py`).
3.  Gemini acts as the "eyes". It analyzes the lighting and pixels to determine the user's **Skin Tone Category** (e.g., Medium), **Undertone** (e.g., Warm), and calculates the closest **Hex Color Code**.

#### Step 3: LLM Generation (Groq / LLaMA)
1.  Once the backend has the skin tone data, it builds a massive "Prompt" (instructions) containing the user's gender and skin metrics.
2.  It sends this prompt to **Groq** (running the LLaMA model).
3.  Groq reads the skin tone and dynamically generates a personalized JSON object containing:
    *   A 3-color palette that compliments that specific skin tone.
    *   A full outfit with specific brands and fabrics.
    *   Matching accessories and hairstyles.
    *   Custom Amazon search queries based on the generated items and user's gender.

#### Step 4: The "AI Cascade" Architecture
*   *You should highlight this as a major technical achievement!*
*   If Groq fails or times out, the system doesn't crash. `analyze.py` is designed with an **AI Cascade**.
*   It utilizes a `try/except` block to gracefully fall back: **Groq → IBM watsonx → Hugging Face → Gemini Text → Local Mock Data**.
*   This ensures 100% uptime for the user.

#### Step 5: Rendering the Results
1.  The backend sends the final, constructed JSON back to the browser.
2.  `app.js` hides the loading screen.
3.  It loops through the JSON data and updates the HTML (e.g., changing the background color of the skin tone swatch, inserting the Amazon links).

---

### Path B: "Text Styling" Flow

1. **User Input:** On the frontend, the user selects "Text Styling" and fills in manual preferences like Body Type, Occasion, Color Preferences, and Budget.
2. **API Request:** `app.js` sends this data as a JSON payload to the `/api/recommend` endpoint.
3. **LLM Generation:** The backend immediately sends these detailed preferences to the AI, instructing it to curate 3 distinct outfits perfectly tailored to those parameters.
4. **Dynamic Search Queries:** The AI also structures precise Amazon search queries for each item, explicitly appending the user's gender to ensure accurate shopping results.
5. **Rendering:** The browser reads the returned JSON and renders a beautiful UI displaying the outfits, general fashion advice, and active shopping links ready to browse.

---

## 💡 Key Selling Points for the Jury
When concluding your presentation, emphasize these technical highlights:

1.  **AI Orchestration:** We aren't just using one AI. We are orchestrating multiple AI models (Vision models for seeing, fast LLMs for text generation) to work together in a single pipeline.
2.  **Robust Fallbacks:** The cascaded API design proves production-readiness. If one provider goes down, the app seamlessly switches to another.
3.  **Dynamic Prompt Engineering:** The system doesn't just ask "give me outfit ideas." It enforces strict JSON formatting from the LLMs so the frontend can securely parse and display complex UI components like color swatches and shopping grids.
4.  **Modern Architecture:** Built on FastAPI (asynchronous and incredibly fast) with a lightweight Vanilla JS frontend, meaning perfectly smooth performance without the bloat of heavy frameworks.
