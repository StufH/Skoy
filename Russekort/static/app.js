(function(){
  const $ = (sel, el=document) => el.querySelector(sel);
  const $$ = (sel, el=document) => Array.from(el.querySelectorAll(sel));
  const esc = (s) => String(s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  const API_BASE = (window.API_BASE || '').replace(/\/+$/, '');
  const PUBLIC_BASE_URL = (window.PUBLIC_BASE_URL || '').replace(/\/+$/, '');
  const api = (path) => `${API_BASE}${path}`;
  const backendLink = (path) => (PUBLIC_BASE_URL ? `${PUBLIC_BASE_URL}${path}` : `${location.origin}${path}`);

  const tabs = {
    create: $('#tab-create'),
    scanner: $('#tab-scanner'),
    album: $('#tab-album'),
    top: $('#tab-top'),
    card: $('#tab-card'),
  };

  const navButtons = $$('header nav button');
  navButtons.forEach(btn => btn.addEventListener('click', () => {
    const tab = btn.getAttribute('data-tab');
    showTab(tab);
    if (tab === 'album') loadAlbum();
    if (tab === 'top') loadTop();
    if (tab === 'scanner') initScannerSupport();
  }));

  function showTab(name) {
    Object.values(tabs).forEach(el => el.classList.add('hidden'));
    const t = tabs[name];
    if (t) t.classList.remove('hidden');
  }

  // State for create/preview
  const canvas = $('#card-canvas');
  const ctx = canvas.getContext('2d');
  const emojiLayer = $('#emoji-layer');
  const createForm = $('#create-form');
  const statusEl = $('#create-status');
  const createdResult = $('#created-result');

  let bgColor = '#f44336';
  let textColor = '#ffffff';
  let fontFamily = 'Arial';
  let baseImage = null; // HTMLImageElement
  let stickers = []; // {emoji, x, y}

  // Drag handling for emojis
  function addEmoji(emoji, x=0.5, y=0.5) {
    const node = document.createElement('div');
    node.className = 'emoji';
    node.textContent = emoji;
    emojiLayer.appendChild(node);
    const obj = {emoji, x, y, el: node};
    stickers.push(obj);
    positionEmoji(obj);
    makeDraggable(obj);
    draw();
  }

  function positionEmoji(obj){
    const rect = canvas.getBoundingClientRect();
    const left = obj.x * rect.width;
    const top = obj.y * rect.height;
    obj.el.style.left = (left - 16) + 'px';
    obj.el.style.top = (top - 16) + 'px';
  }

  function makeDraggable(obj){
    let dragging = false;
    let start = {x:0,y:0};
    const onDown = (e) => {
      dragging = true;
      obj.el.setPointerCapture?.(e.pointerId);
      start = {x: e.clientX, y: e.clientY};
      e.preventDefault();
    };
    const onMove = (e) => {
      if (!dragging) return;
      const rect = canvas.getBoundingClientRect();
      const dx = e.clientX - start.x;
      const dy = e.clientY - start.y;
      const left = parseFloat(obj.el.style.left||'0') + dx;
      const top = parseFloat(obj.el.style.top||'0') + dy;
      obj.el.style.left = left + 'px';
      obj.el.style.top = top + 'px';
      start = {x: e.clientX, y: e.clientY};
      // Update normalized coords
      obj.x = (left + 16) / rect.width;
      obj.y = (top + 16) / rect.height;
      draw();
    };
    const onUp = (e) => { dragging = false; };
    obj.el.addEventListener('pointerdown', onDown);
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
  }

  function wrapText(text, maxWidth, font) {
    ctx.font = font;
    const words = (text||'').split(' ');
    const lines = [];
    let line = '';
    for (let n=0;n<words.length;n++){
      const testLine = line ? (line + ' ' + words[n]) : words[n];
      const metrics = ctx.measureText(testLine);
      const width = metrics.width;
      if (width > maxWidth && n>0){
        lines.push(line);
        line = words[n];
      } else {
        line = testLine;
      }
    }
    if (line) lines.push(line);
    return lines;
  }

  function draw(){
    const W = canvas.width, H = canvas.height;
    // Background
    ctx.fillStyle = bgColor || '#f44336';
    ctx.fillRect(0,0,W,H);

    // Image
    if (baseImage){
      // cover fit
      const img = baseImage;
      const arImg = img.width / img.height;
      const arCan = W / H;
      let dw, dh, dx, dy;
      if (arImg > arCan){
        dh = H; dw = dh * arImg; dx = (W - dw)/2; dy = 0;
      } else {
        dw = W; dh = dw / arImg; dx = 0; dy = (H - dh)/2;
      }
      ctx.globalAlpha = 0.9;
      ctx.drawImage(img, dx, dy, dw, dh);
      ctx.globalAlpha = 1;
      // overlay for text readability
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(0,0,W,H);
    }

    ctx.fillStyle = textColor || '#fff';
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';

    const displayName = createForm.display_name.value || '';
    const title = createForm.russ_title.value || '';
    const line = createForm.line.value || '';
    const quote = createForm.quote.value || '';

    const padding = 16;
    const maxTextWidth = W - padding*2;

    ctx.font = `bold 28px ${fontFamily}`;
    ctx.fillText(displayName, padding, padding);

    ctx.font = `600 20px ${fontFamily}`;
    ctx.fillText(title, padding, padding + 36);

    ctx.font = `16px ${fontFamily}`;
    ctx.fillText(line, padding, padding + 60);

    if (quote){
      ctx.font = `italic 14px ${fontFamily}`;
      const lines = wrapText('"' + quote + '"', maxTextWidth, ctx.font);
      let y = H - padding - lines.length*18 - 48;
      lines.forEach((ln,i)=>{ ctx.fillText(ln, padding, y + i*18); });
    }

    // Contacts
    const snapchat = createForm.snapchat.value.trim();
    const instagram = createForm.instagram.value.trim();
    const phone = createForm.phone.value.trim();

    let y = H - padding - 48;
    ctx.font = `14px ${fontFamily}`;
    if (snapchat){ ctx.fillText('Snap: ' + snapchat, padding, y); y += 18; }
    if (instagram){ ctx.fillText('IG: ' + instagram, padding, y); y += 18; }
    if (phone){ ctx.fillText('Tlf: ' + phone, padding, y); y += 18; }

    // Stickers: draw emoji onto canvas as well for export
    const rect = canvas.getBoundingClientRect();
    stickers.forEach(s => {
      const x = s.x * W, y = s.y * H;
      ctx.font = '32px serif';
      ctx.fillText(s.emoji, x-16, y-16);
    });
  }

  // Hook form controls
  createForm.bg_color.addEventListener('input', (e) => { bgColor = e.target.value; draw(); });
  createForm.text_color.addEventListener('input', (e) => { textColor = e.target.value; draw(); });
  createForm.font.addEventListener('change', (e) => { fontFamily = e.target.value; draw(); });
  ['display_name','russ_title','line','quote','snapchat','instagram','phone'].forEach(n =>
    createForm[n].addEventListener('input', draw)
  );
  createForm.image.addEventListener('change', () => {
    const file = createForm.image.files?.[0];
    if (!file){ baseImage = null; draw(); return; }
    const img = new Image();
    img.onload = () => { baseImage = img; draw(); };
    img.src = URL.createObjectURL(file);
  });

  // Emoji palette
  $('#emoji-palette').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-emoji]');
    if (!b) return;
    addEmoji(b.dataset.emoji, 0.8, 0.2);
  });

  // Download PNG of canvas
  $('#download-png').addEventListener('click', () => {
    const a = document.createElement('a');
    a.download = 'russekort.png';
    a.href = canvas.toDataURL('image/png');
    a.click();
  });

  // Submit create form
  createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    statusEl.textContent = 'Lagrer…';
    const fd = new FormData();
    fd.append('display_name', createForm.display_name.value);
    fd.append('russ_title', createForm.russ_title.value);
    fd.append('line', createForm.line.value);
    fd.append('quote', createForm.quote.value);

    const contact = {
      snapchat: createForm.snapchat.value.trim() || undefined,
      instagram: createForm.instagram.value.trim() || undefined,
      phone: createForm.phone.value.trim() || undefined,
    };
    fd.append('contact_json', JSON.stringify(contact));

    fd.append('bg_color', bgColor);
    fd.append('text_color', textColor);
    fd.append('font', fontFamily);

    const stickersData = stickers.map(s => ({emoji: s.emoji, x: s.x, y: s.y}));
    fd.append('stickers_json', JSON.stringify(stickersData));

    if (createForm.image.files && createForm.image.files[0]){
      fd.append('image', createForm.image.files[0]);
    }

    try {
      const res = await fetch(api('/api/cards'), {method: 'POST', body: fd});
      if (!res.ok) throw new Error('Kunne ikke lagre kort');
      const card = await res.json();
      statusEl.textContent = 'Lagret!';
      showCreated(card);
    } catch (err){
      console.error(err);
      statusEl.textContent = 'Feil: ' + err.message;
    }
  });

  function showCreated(card){
    createdResult.classList.remove('hidden');
    const link = backendLink(`/card/${card.id}`);
    createdResult.innerHTML = `
      <p>Kort laget: <a href="${link}">${link}</a></p>
      <div class="row">
        <img src="${api(`/api/cards/${card.id}/qrcode`)}" alt="QR" />
        <button type="button" class="primary" id="open-card">Åpne kort</button>
      </div>
    `;
    $('#open-card').addEventListener('click', () => {
      if (API_BASE) {
        window.open(link, '_blank');
      } else {
        history.pushState({}, '', `/card/${card.id}`);
        renderCardView(card.id);
      }
    });
  }

  // Scanner
  const scannerInfo = $('#scanner-support');
  const video = $('#preview');
  let stream = null;
  let scanTimer = null;
  let barcodeDetector = null;

  function initScannerSupport(){
    if ('BarcodeDetector' in window){
      scannerInfo.textContent = 'Klar til å skanne. Trykk Start kamera.';
    } else {
      scannerInfo.innerHTML = 'Skanner støttes ikke i denne nettleseren. Prøv Chrome, eller åpne QR-koden manuelt.';
    }
  }

  $('#start-scan').addEventListener('click', async () => {
    if (!('BarcodeDetector' in window)) { initScannerSupport(); return; }
    try {
      barcodeDetector = new window.BarcodeDetector({formats: ['qr_code']});
    } catch(e){
      scannerInfo.textContent = 'Kunne ikke starte skanner: ' + e.message;
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: 'environment'}});
      video.srcObject = stream;
      await video.play();
      scannerInfo.textContent = 'Skanner…';
      startDetecting();
    } catch (e){
      scannerInfo.textContent = 'Kameratilgang nektet eller ikke tilgjengelig.';
    }
  });

  $('#stop-scan').addEventListener('click', stopScanning);

  function stopScanning(){
    if (scanTimer){ clearInterval(scanTimer); scanTimer = null; }
    if (video){ video.pause(); }
    if (stream){ stream.getTracks().forEach(t => t.stop()); stream = null; }
    scannerInfo.textContent = 'Stoppet.';
  }

  async function startDetecting(){
    if (!barcodeDetector) return;
    if (scanTimer) clearInterval(scanTimer);
    scanTimer = setInterval(async () => {
      try {
        const barcodes = await barcodeDetector.detect(video);
        if (barcodes && barcodes.length){
          const raw = barcodes[0].rawValue || '';
          onQrDetected(raw);
          stopScanning();
        }
      } catch (e){ /* ignore */ }
    }, 350);
  }

  async function onQrDetected(text){
    const resultEl = $('#scan-result');
    resultEl.textContent = 'QR: ' + text;
    const m = text.match(/\/card\/([a-f0-9]{16,})/i);
    if (m){
      const id = m[1];
      await fetch(api(`/api/cards/${id}/scan`), {method: 'POST'}).catch(()=>{});
      addToAlbum(id);
      if (API_BASE) {
        window.open(backendLink(`/card/${id}`), '_blank');
      } else {
        history.pushState({}, '', `/card/${id}`);
        renderCardView(id);
      }
    } else {
      window.open(text, '_blank');
    }
  }

  // Album
  const albumKey = 'russekort_album_v1';
  function getAlbum(){
    try { return JSON.parse(localStorage.getItem(albumKey) || '[]'); } catch { return []; }
  }
  function saveAlbum(arr){ localStorage.setItem(albumKey, JSON.stringify(arr)); }
  function addToAlbum(id){
    const arr = getAlbum();
    if (!arr.includes(id)) { arr.unshift(id); saveAlbum(arr); }
    loadAlbum();
  }
  function removeFromAlbum(id){
    const arr = getAlbum().filter(x => x !== id);
    saveAlbum(arr);
    loadAlbum();
  }
  async function loadAlbum(){
    const grid = $('#album-grid');
    grid.innerHTML = '';
    const ids = getAlbum();
    if (!ids.length){ grid.innerHTML = '<p>Ingen kort i albumet enda.</p>'; return; }
    for (const id of ids){
      try {
        const res = await fetch(api(`/api/cards/${id}`));
        if (!res.ok) throw new Error();
        const card = await res.json();
        const div = document.createElement('div');
        div.className = 'card-tile';
        div.innerHTML = `
          <img src="${card.image_url || '/static/placeholder.svg'}" alt="" />
          <div class="name">${esc(card.display_name||'Ukjent')}</div>
          <div class="row">
            <button data-open="${card.id}">Åpne</button>
            <button data-remove="${card.id}">Fjern</button>
          </div>
        `;
        grid.appendChild(div);
      } catch {
        // skip
      }
    }
    grid.addEventListener('click', (e) => {
      const openBtn = e.target.closest('button[data-open]');
      if (openBtn){
        const id = openBtn.getAttribute('data-open');
        history.pushState({}, '', `/card/${id}`);
        renderCardView(id);
      }
      const remBtn = e.target.closest('button[data-remove]');
      if (remBtn){ removeFromAlbum(remBtn.getAttribute('data-remove')); }
    }, {once: true});
  }

  // Top
  async function loadTop(){
    const list = $('#top-list');
    list.innerHTML = '';
    try {
      const res = await fetch(api('/api/top'));
      const items = await res.json();
      items.forEach((it, idx) => {
        const row = document.createElement('div');
        row.className = 'top-item';
        row.innerHTML = `
          <div>#${idx+1}</div>
          <img src="${it.image_url || '/static/placeholder.svg'}" alt="" />
          <div style="flex:1">
            <div><strong>${esc(it.display_name || 'Ukjent')}</strong></div>
            <div>${it.scan_count} skann</div>
          </div>
          <button data-open="${it.id}">Åpne</button>
        `;
        list.appendChild(row);
      });
      list.addEventListener('click', (e) => {
        const b = e.target.closest('button[data-open]');
        if (b){
          const id = b.getAttribute('data-open');
          history.pushState({}, '', `/card/${id}`);
          renderCardView(id);
        }
      }, {once: true});
    } catch (e){
      list.textContent = 'Kunne ikke laste toppliste.';
    }
  }

  // Card deep link view
  async function renderCardView(id){
    if (API_BASE) {
      window.open(backendLink(`/card/${id}`), '_blank');
      return;
    }
    showTab('card');
    const view = $('#card-view');
    view.innerHTML = '<p>Laster…</p>';
    try {
      const res = await fetch(`/api/cards/${id}`);
      if (!res.ok) throw new Error('Not found');
      const card = await res.json();
      addToAlbum(id);
      // Build a rendered canvas for the card details
      const w = 760, h = 444;
      const cv = document.createElement('canvas');
      cv.width = w; cv.height = h;
      const c = cv.getContext('2d');
      // background
      c.fillStyle = card.bg_color || '#f44336';
      c.fillRect(0,0,w,h);
      // image
      await new Promise(resolve => {
        if (!card.image_url) return resolve();
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          const arImg = img.width/img.height; const arCan = w/h;
          let dw, dh, dx, dy;
          if (arImg > arCan){ dh=h; dw=dh*arImg; dx=(w-dw)/2; dy=0; }
          else { dw=w; dh=dw/arImg; dx=0; dy=(h-dh)/2; }
          c.globalAlpha = 0.9; c.drawImage(img, dx, dy, dw, dh); c.globalAlpha=1;
          c.fillStyle = 'rgba(0,0,0,0.25)'; c.fillRect(0,0,w,h);
          resolve();
        };
        img.onerror = () => resolve();
        img.src = card.image_url;
      });
      // text
      c.fillStyle = card.text_color || '#fff';
      c.textBaseline = 'top'; c.textAlign='left';
      const pad = 18; const maxW = w - pad*2;
      c.font = `bold 34px ${card.font || 'Arial'}`;
      c.fillText(card.display_name||'', pad, pad);
      c.font = `600 22px ${card.font || 'Arial'}`;
      c.fillText(card.russ_title||'', pad, pad+42);
      c.font = `16px ${card.font || 'Arial'}`;
      c.fillText(card.line||'', pad, pad+70);
      if (card.quote){
        c.font = `italic 16px ${card.font || 'Arial'}`;
        const lines = (card.quote||'').match(/.{1,38}(\s|$)/g)||[card.quote];
        let y = h - pad - lines.length*20 - 56;
        lines.forEach((ln,i)=> c.fillText(ln.trim(), pad, y + i*20));
      }
      // contacts
      let y = h - pad - 56; c.font = `16px ${card.font || 'Arial'}`;
      const ct = card.contact || {};
      if (ct.snapchat) { c.fillText('Snap: ' + ct.snapchat, pad, y); y+=20; }
      if (ct.instagram){ c.fillText('IG: ' + ct.instagram, pad, y); y+=20; }
      if (ct.phone){ c.fillText('Tlf: ' + ct.phone, pad, y); y+=20; }
      // stickers
      const sts = card.stickers || [];
      sts.forEach(s => { c.font='32px serif'; c.fillText(s.emoji||'⭐', s.x*w-16, s.y*h-16); });

      view.innerHTML = '';
      const link = `${location.origin}/card/${id}`;
      view.appendChild(cv);
      const actions = document.createElement('div');
      actions.className = 'actions';
      actions.innerHTML = `
        <a class="primary" href="${api(`/api/cards/${id}/qrcode`)}" target="_blank">Last ned QR</a>
        <button id="copy-link" type="button">Kopier lenke</button>
        <button id="add-album" type="button">Lagre i album</button>
      `;
      view.appendChild(actions);
      const qr = document.createElement('div');
      qr.className = 'qr';
      qr.innerHTML = `<p>Skann denne for å samle kortet:</p><img src="${api(`/api/cards/${id}/qrcode`)}" alt="QR" />`;
      view.appendChild(qr);
      $('#copy-link').addEventListener('click', async () => {
        await navigator.clipboard.writeText(link).catch(()=>{});
      });
      $('#add-album').addEventListener('click', () => addToAlbum(id));
    } catch (e){
      view.innerHTML = '<p>Fant ikke kortet.</p>';
    }
  }

  // Deep link routing
  function handleInitialRoute(){
    const m = location.pathname.match(/^\/card\/([a-f0-9]{16,})/i);
    if (m){ renderCardView(m[1]); }
    else { showTab('create'); }
  }

  // Resize observer to keep emoji overlay aligned
  const ro = new ResizeObserver(() => {
    stickers.forEach(positionEmoji);
  });
  ro.observe(canvas);

  // Initial draw
  draw();
  handleInitialRoute();
})();
