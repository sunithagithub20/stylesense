/* ============================================================
   StyleSense – app.js
   Handles: Settings, Navigation, Upload, Analysis, Results, Shopping
   ============================================================ */

const API_BASE = '';  // Same origin (FastAPI serves this)

// ─── State ───────────────────────────────────────────────────
const state = {
  geminiKey: '',
  groqKey: '',
  hfToken: '',
  ibmKey: '',
  ibmProjectId: '',
  gender: 'male',
  photoFile: null,
  result: null,
};

// ─── Color Name → Approximate Hex Lookup ─────────────────────
const COLOR_MAP = {
  'navy blue': '#1E3A5F', 'navy': '#001F5B',
  'royal blue': '#4169E1', 'cobalt': '#0047AB',
  'light grey': '#B0B0B0', 'grey': '#808080', 'gray': '#808080',
  'dark brown': '#5C3317', 'brown': '#8B4513', 'tan': '#D2B48C',
  'white': '#F5F5F5', 'black': '#1A1A1A', 'cream': '#FFFDD0',
  'beige': '#F5F5DC', 'ivory': '#FFFFF0', 'camel': '#C19A6B',
  'olive': '#808000', 'olive green': '#6B8E23',
  'terracotta': '#E2725B', 'rust': '#B7410E',
  'burgundy': '#800020', 'maroon': '#800000', 'wine': '#722f37',
  'emerald': '#50C878', 'emerald green': '#50C878', 'forest green': '#228B22',
  'gold': '#FFD700', 'yellow': '#FFD700',
  'peach': '#FFCBA4', 'coral': '#FF7F7F',
  'lavender': '#E6E6FA', 'purple': '#800080',
  'pink': '#FFC0CB', 'hot pink': '#FF69B4',
  'orange': '#FFA500', 'burnt orange': '#CC5500',
  'teal': '#008080', 'turquoise': '#40E0D0',
  'charcoal': '#36454F', 'off-white': '#FAF9F6',
};

function colorToHex(name) {
  if (!name) return '#888888';
  const lower = name.toLowerCase().trim();
  if (lower.startsWith('#')) return lower;
  return COLOR_MAP[lower] || COLOR_MAP[lower.split(' ')[0]] || '#888888';
}

// ─── DOM References ──────────────────────────────────────────
const $ = id => document.getElementById(id);

// ─── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initTabs();
  initUpload();
  initGender();
  initAnalyze();
  initRecommend();
});

// ─── Tabs ────────────────────────────────────────────────────
function initTabs() {
  const tabP = $('tabPhoto');
  const tabT = $('tabText');
  const panP = $('uploadPanel');
  const panT = $('textPanel');

  if (!tabP || !tabT) return;

  tabP.onclick = () => {
    tabP.classList.add('active'); tabT.classList.remove('active');
    panP.classList.remove('hidden'); panT.classList.add('hidden');
  };
  tabT.onclick = () => {
    tabT.classList.add('active'); tabP.classList.remove('active');
    panT.classList.remove('hidden'); panP.classList.add('hidden');
  };
}

// ─── Navigation ──────────────────────────────────────────────
function initNav() {
  const links = document.querySelectorAll('.nav-link');
  const header = $('mainHeader');

  links.forEach(l => {
    l.onclick = e => {
      links.forEach(x => x.classList.remove('active'));
      l.classList.add('active');
    };
  });

  // Sticky header shadow
  window.addEventListener('scroll', () => {
    header.style.boxShadow = window.scrollY > 20
      ? '0 4px 24px rgba(0,0,0,.4)' : '';
  });

  // Scroll-spy
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    let cur = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) cur = s.id;
    });
    links.forEach(l => {
      l.classList.toggle('active', l.getAttribute('href') === '#' + cur);
    });
  }, { passive: true });
}

// ─── Gender ──────────────────────────────────────────────────
function initGender() {
  document.querySelectorAll('.gender-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.gender = btn.dataset.g;
    };
  });
}

// ─── Upload ──────────────────────────────────────────────────
function initUpload() {
  const zone = $('dropZone');
  const input = $('photoInput');
  const btn = $('browseBtn');

  btn.onclick = e => { e.stopPropagation(); input.click(); };

  input.onchange = () => {
    if (input.files[0]) handleFile(input.files[0]);
  };

  zone.addEventListener('dragover', e => {
    e.preventDefault(); zone.classList.add('drag-over');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) handleFile(f);
  });
}

function handleFile(file) {
  if (file.size > 10 * 1024 * 1024) {
    alert('File too large. Please upload an image under 10MB.');
    return;
  }
  state.photoFile = file;

  // Show preview in drop zone
  const reader = new FileReader();
  reader.onload = e => {
    const prev = $('photoPreview');
    const inner = $('dropInner');
    prev.src = e.target.result;
    prev.classList.remove('hidden');
    inner.classList.add('hidden');

    // Show preview panel
    const lg = $('previewLarge');
    lg.src = e.target.result;
    $('previewEmpty').classList.add('hidden');
    $('previewPhoto').classList.remove('hidden');
  };
  reader.readAsDataURL(file);

  $('analyzeBtn').disabled = false;
}

// ─── Analyze ─────────────────────────────────────────────────
function initAnalyze() {
  $('analyzeBtn').onclick = runAnalysis;
  $('tryAgainBtn').onclick = resetToUpload;
}

async function runAnalysis() {
  if (!state.photoFile) return;

  // Show loading
  showLoading();

  try {
    const fd = new FormData();
    fd.append('file', state.photoFile);
    fd.append('gender', state.gender);
    // Keys are picked up from .env on backend

    // Step indicators
    setLoadStep(1);
    await delay(600);
    setLoadStep(2);

    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      body: fd,
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);

    setLoadStep(3);
    await delay(400);

    const data = await res.json();
    state.result = data;

    hideLoading();
    showResults(data);
  } catch (err) {
    console.error(err);
    hideLoading();
    alert(`Analysis failed: ${err.message}.\n\nMake sure the backend is running on http://localhost:8000`);
  }
}

function setLoadStep(n) {
  for (let i = 1; i <= 3; i++) {
    const el = $(`ls${i}`);
    if (i < n) { el.classList.add('done'); el.classList.remove('active'); }
    if (i === n) { el.classList.add('active'); el.classList.remove('done'); }
    if (i > n) { el.classList.remove('active', 'done'); }
  }
}

function showLoading() {
  $('loadingOverlay').classList.remove('hidden');
  setLoadStep(1);
}
function hideLoading() {
  $('loadingOverlay').classList.add('hidden');
}

// ─── Render Results ──────────────────────────────────────────
function showResults(data) {
  // Hide upload panels, show results
  $('uploadPanel').classList.add('hidden');
  $('resultsSection').classList.remove('hidden');

  // Scroll to results
  $('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });

  renderSkinTone(data.skin_tone);
  renderOutfit(data);
  renderStyleDetails(data);
  renderPalette(data);
  renderShopping(data.shopping_items);
}

function renderSkinTone(st) {
  $('skinSwatch').style.background = st.hex || '#C68642';
  $('skinCat').textContent = `${st.category || 'Medium'} · ${st.undertone || 'Warm'} Undertone`;
  $('skinDesc').textContent = st.description || '';

  const rgb = st.rgb || {};
  $('skinDetails').innerHTML = [
    `<span class="skin-tag">Hex: ${st.hex || '#C68642'}</span>`,
    rgb.r !== undefined ? `<span class="skin-tag">RGB(${rgb.r}, ${rgb.g}, ${rgb.b})</span>` : '',
    st.category ? `<span class="skin-tag">${st.category}</span>` : ''
  ].join('');
}

function renderOutfit(data) {
  // Dress codes
  const codes = data.dress_code || [];
  $('dressCodes').innerHTML = codes.map(c =>
    `<span class="dress-tag">${c}</span>`
  ).join('');

  // Suggested outfit
  $('suggestedOutfit').textContent = data.suggested_outfit || '';

  // Clothing items
  const items = data.clothing_items || [];
  $('clothingItems').innerHTML = items.map(ci => `
    <div class="clothing-item">
      <div class="ci-name">${ci.item || ''}</div>
      <div class="ci-details">
        ${ci.color ? `<div class="ci-row"><span class="ci-label">Color:</span> ${ci.color}</div>` : ''}
        ${ci.type ? `<div class="ci-row"><span class="ci-label">Type:</span> ${ci.type}</div>` : ''}
        ${ci.brand ? `<div class="ci-row"><span class="ci-label">Brand:</span> ${ci.brand}</div>` : ''}
        ${ci.fabric ? `<div class="ci-row"><span class="ci-label">Fabric:</span> ${ci.fabric}</div>` : ''}
      </div>
    </div>
  `).join('');
}

function renderStyleDetails(data) {
  // Hairstyle
  const hs = data.hairstyle || {};
  $('hairstyleName').textContent = hs.style || '';
  $('hairstyleHow').textContent = hs.how_to || '';

  // Accessories
  const accs = data.accessories || [];
  $('accessoriesList').innerHTML = accs.map((a, i) => `
    <div class="acc-item">
      <span class="acc-num">${i + 1}</span>
      <span>${a}</span>
    </div>
  `).join('');
}

function renderPalette(data) {
  const pal = data.color_palette || {};
  const entries = [
    { cat: 'Primary', name: pal.primary || '' },
    { cat: 'Secondary', name: pal.secondary || '' },
    { cat: 'Accent', name: pal.accent || '' },
  ].filter(e => e.name);

  $('paletteSwatches').innerHTML = entries.map(e => `
    <div class="palette-row">
      <div class="palette-dot" style="background:${colorToHex(e.name)}"></div>
      <div class="palette-info">
        <div class="palette-cat">${e.cat}</div>
        <div class="palette-name">${e.name}</div>
      </div>
    </div>
  `).join('');

  $('whyItWorks').textContent = data.why_it_works || '';
}

function renderTextResults(data) {
  // Hide upload/text panels
  $('uploadPanel').classList.add('hidden');
  const textPan = $('textPanel');
  if (textPan) textPan.classList.add('hidden');

  const resSec = $('resultsSection');
  resSec.classList.remove('hidden');
  resSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Hide the photo-specific cards
  $('skinToneCard').style.display = 'none';
  $('paletteCard').style.display = 'none';

  // We reuse the outfitCard for text results
  const recs = data.recommendations || [];

  let html = '';
  recs.forEach((r, i) => {
    html += `
      <div class="mb-12">
        <h3 style="font-size:1.2rem; color:var(--text); margin-bottom:8px;">${i + 1}. ${r.name || 'Outfit'}</h3>
        <p class="result-text">${r.description || ''}</p>
        <div class="result-label mt-8">ITEMS</div>
        <ul style="color:var(--text-sub); margin-left:20px; margin-bottom:12px;">
          ${(r.items || []).map(item => `<li>${item}</li>`).join('')}
        </ul>
        <div class="result-label">COLORS & TIPS</div>
        <p class="result-text" style="font-size:0.9rem;"><strong>Colors:</strong> ${r.color_scheme || ''}</p>
        <p class="result-text" style="font-size:0.9rem;"><strong>Tip:</strong> ${r.styling_tips || ''}</p>
      </div>
      <hr style="border:0; border-top:1px solid rgba(255,255,255,0.05); margin: 16px 0;">
    `;
  });

  $('outfitCard').innerHTML = `
    <div class="result-label">YOUR TEXT RECOMMENDATIONS</div>
    ${html}
  `;

  // General advice in the right column
  $('hairstyleCard').innerHTML = `
    <div class="result-label">GENERAL ADVICE</div>
    <p class="result-text">${data.general_advice || ''}</p>
    <div class="result-label mt-12">COLOR SUGGESTIONS</div>
    <p class="result-text">${data.color_suggestions || ''}</p>
  `;

  // Render shopping links
  $('shopSection').classList.remove('hidden');
  renderShopping(data.shopping_items);
}

function renderShopping(items) {
  if (!items || items.length === 0) {
    $('shopSection').classList.add('hidden');
    return;
  }
  const icons = ['👔', '👗', '👟', '👜', '🎩', '👒', '💍', '🧥'];
  $('shopGrid').innerHTML = items.map((item, i) => {
    const q = encodeURIComponent(item.query || item.name);
    const url = `https://www.amazon.in/s?k=${q}`;
    return `
      <div class="shop-card">
        <div class="shop-icon">${icons[i % icons.length]}</div>
        <div class="shop-name">${item.name}</div>
        <a class="shop-btn" href="${url}" target="_blank" rel="noopener">
          🔗 Shop Now
        </a>
      </div>
    `;
  }).join('');
}

// ─── Reset ───────────────────────────────────────────────────
function resetToUpload() {
  // Reset state
  state.photoFile = null;
  state.result = null;

  // Reset UI
  $('photoInput').value = '';
  $('photoPreview').classList.add('hidden');
  $('dropInner').classList.remove('hidden');
  $('analyzeBtn').disabled = true;
  $('previewEmpty').classList.remove('hidden');
  $('previewPhoto').classList.add('hidden');

  $('resultsSection').classList.add('hidden');
  $('uploadPanel').classList.remove('hidden');

  window.scrollTo({ top: $('try-it').offsetTop - 80, behavior: 'smooth' });
}

// ─── Text Recommend ──────────────────────────────────────────
function initRecommend() {
  const btn = $('recommendBtn');
  if (btn) btn.onclick = runRecommend;
}

async function runRecommend() {
  const payload = {
    body_type: $('textBodyType').value.trim() || 'Average',
    style_preference: $('textStylePref').value.trim() || 'Casual',
    occasion: $('textOccasion').value.trim() || 'Everyday',
    color_palette: $('textColor').value.trim() || 'Neutral',
    budget: $('textBudget').value.trim() || 'Mid-range',
    gender: state.gender || 'unisex',
    season: 'Current'
  };

  showLoading();
  $('loadingMsg').textContent = 'Analyzing text preferences with AI...';

  try {
    setLoadStep(1);
    await delay(400);
    setLoadStep(2);

    const res = await fetch(`${API_BASE}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);

    setLoadStep(3);
    await delay(300);

    const data = await res.json();
    hideLoading();
    renderTextResults(data);
  } catch (err) {
    console.error(err);
    hideLoading();
    alert(`Generation failed: ${err.message}`);
  }
}

// ─── Helpers ─────────────────────────────────────────────────
const delay = ms => new Promise(r => setTimeout(r, ms));
