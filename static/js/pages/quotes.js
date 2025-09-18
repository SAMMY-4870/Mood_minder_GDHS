// quotes.js

document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('quotesList');
  const loadBtn = document.getElementById('loadQuotes');
  const shuffleBtn = document.getElementById('shuffleQuotes');

  function render(quotes){
    list.innerHTML = '';
    quotes.forEach(q => {
      const item = document.createElement('div');
      item.className = 'alert alert-success';
      item.innerHTML = `<strong>${q.quote || ''}</strong><div class="fst-italic">— ${q.author || 'Unknown'}</div>`;
      list.appendChild(item);
    });
  }

  async function fetchQuotes(){
    const res = await fetch('/api/random-quotes?limit=10');
    const data = await res.json();
    render(data.items || []);
  }

  function shuffle(){
    const children = Array.from(list.children);
    for(let i=children.length-1;i>0;i--){
      const j=Math.floor(Math.random()*(i+1));
      list.appendChild(children[j]);
      children.splice(j,1);
    }
  }

  loadBtn && loadBtn.addEventListener('click', fetchQuotes);
  shuffleBtn && shuffleBtn.addEventListener('click', shuffle);

  // auto-load on page enter
  if(loadBtn) fetchQuotes();
});
