// images.js

document.addEventListener('DOMContentLoaded', function () {
  const grid = document.getElementById('imagesGrid');
  const loadBtn = document.getElementById('loadImages');
  const refreshBtn = document.getElementById('refreshImages');

  function render(items){
    grid.innerHTML = '';
    items.forEach((it) => {
      const col = document.createElement('div');
      col.className = 'col-12 col-md-6 col-lg-4';
      col.innerHTML = `<div class="card h-100">
                         <img class="card-img-top img-large" src="${it.url}" alt="img" data-url="${it.url}"/>
                       </div>`;
      grid.appendChild(col);
    });

    // click to preview with modal and download
    grid.querySelectorAll('img[data-url]').forEach(img => {
      img.addEventListener('click', () => {
        const src = img.getAttribute('data-url');
        const modalImg = document.getElementById('modalImage');
        const dl = document.getElementById('downloadImage');
        if(modalImg) {
          modalImg.src = src;
          modalImg.setAttribute('data-fullsrc', src);
        }
        if(dl){ 
          dl.href = src + '?download=1';
          dl.setAttribute('download', src.split('/').pop() || 'image.jpg');
        }
        if(window.bootstrap){
          const modal = new bootstrap.Modal(document.getElementById('imageModal'));
          modal.show();
        }
      });
    });
  }

  async function load(){
    try{
      const res = await fetch('/api/random-images?limit=12', {cache:'no-store'});
      if(!res.ok) throw new Error('Network error');
      const data = await res.json();
      render(Array.isArray(data.items) ? data.items : []);
    }catch(err){
      grid.innerHTML = '<div class="col-12"><div class="alert alert-danger">Failed to load images.</div></div>';
    }
  }

  loadBtn && loadBtn.addEventListener('click', load);
  refreshBtn && refreshBtn.addEventListener('click', load);

  if(loadBtn) load();
});
