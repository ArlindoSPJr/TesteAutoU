async function postJSON(url, data){
  const api_url = "https://teste-auto-u.vercel.app" + url;
  const res = await fetch(api_url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
  if(!res.ok){ throw new Error(await res.text()); }
  return await res.json();
}

async function postFile(url, file){
  const api_url = "https://teste-auto-u.vercel.app" + url;
  const fd = new FormData();
  fd.append('file', file);
  const res = await fetch(api_url, { method:'POST', body: fd });
  if(!res.ok){ throw new Error(await res.text()); }
  return await res.json();
}

function showResult(r){
  document.getElementById('result').hidden = false;
  document.getElementById('category').textContent = r.category;
  document.getElementById('confidence').textContent = (r.confidence*100).toFixed(1) + '%';
  document.getElementById('reply').textContent = r.reply;
}


function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `
      <span class="loading-spinner"></span>
      Processando...
    `;
    button.disabled = true;
    button.classList.add('loading');
  } else {
    button.innerHTML = button.dataset.originalText;
    button.disabled = false;
    button.classList.remove('loading');
  }
}

const uploadForm = document.getElementById('upload-form');
uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = document.getElementById('file').files[0];
  const submitButton = uploadForm.querySelector('button[type="submit"]');
  
  if(!file){ 
    alert('Selecione um arquivo .txt ou .pdf'); 
    return; 
  }
  
  try {
    setButtonLoading(submitButton, true);
    const r = await postFile('/upload', file);
    showResult(r);
  } catch(err) { 
    alert('Erro: ' + err.message); 
  } finally {
    setButtonLoading(submitButton, false);
  }
});

const textForm = document.getElementById('text-form');
textForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = document.getElementById('email-text').value.trim();
  const submitButton = textForm.querySelector('button[type="submit"]');
  
  if(!text){ 
    alert('Cole o texto do e-mail.'); 
    return; 
  }
  
  try {
    setButtonLoading(submitButton, true);
    const r = await postJSON('/classify', { text });
    showResult(r);
  } catch(err) { 
    alert('Erro: ' + err.message); 
  } finally {
    setButtonLoading(submitButton, false);
  }
});

// Versão alternativa mais simples (se preferir)
function toggleButtonLoading(button, isLoading, loadingText = 'Carregando...') {
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText;
    button.disabled = false;
  }
}