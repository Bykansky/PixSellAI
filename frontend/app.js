const uploadBtn = document.getElementById('upload');
const fileInput = document.getElementById('file');
const productInput = document.getElementById('product_id');
const cards = document.getElementById('cards');

uploadBtn.onclick = async () => {
  const file = fileInput.files[0];
  const product_id = productInput.value || 'demo-sku';
  if(!file) return alert('Choose a file');
  const form = new FormData();
  form.append('product_id', product_id);
  form.append('file', file);
  const res = await fetch('/api/generate', { method:'POST', body: form });
  const data = await res.json();
  if(data.job_id){
    // fetch generations
    setTimeout(async ()=>{
      const gens = await (await fetch(`/api/product/${product_id}/generations`)).json();
      renderCards(gens);
    }, 600);
  } else alert('error');
}

function renderCards(gens){
  cards.innerHTML = '';
  gens.forEach(g => {
    const div = document.createElement('div');
    div.className = 'card';
    const img = document.createElement('img');
    img.src = g.image_uri;
    const btns = document.createElement('div');
    btns.className = 'btns';
    const like = document.createElement('button');
    like.textContent = '♥ Save';
    like.onclick = async ()=>{
      await fetch('/api/swipe', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:1,generation_id:g.id,liked:true})});
      like.textContent = 'Saved';
    };
    const nope = document.createElement('button');
    nope.className='deny';
    nope.textContent='✕';
    nope.onclick = async ()=>{
      await fetch('/api/swipe', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:1,generation_id:g.id,liked:false})});
      div.style.opacity=0.4;
    };
    btns.appendChild(like); btns.appendChild(nope);
    div.appendChild(img); div.appendChild(btns);
    cards.appendChild(div);
  })
}
