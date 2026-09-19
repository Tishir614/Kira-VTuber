let kiraStore={catalog:{voices:[],ai:[],plugins:[]},installed:{}};
async function loadCatalog(){try{const r=await fetch('/catalog',{cache:'no-store'});if(!r.ok)throw Error(await r.text());kiraStore=await r.json();renderStore('voices','voiceCatalogList');renderStore('ai','aiCatalogList');renderStore('plugins','pluginCatalogList')}catch(e){console.error('Kira Store',e)}}
function meta(x){return [x.size_mb?'≈ '+x.size_mb+' MB':'',x.ram_gb?'RAM '+x.ram_gb+' GB':'',x.speed?'⚡ '+x.speed:'',x.quality?'✦ '+x.quality:'',x.style||'',x.category||''].filter(Boolean).map(v=>'<span>'+v+'</span>').join('')}
function renderStore(kind,target){const el=document.getElementById(target);if(!el)return;let items=kiraStore.catalog[kind]||[];if(kind==='voices')items=items.filter(x=>x.gender==='female');const st=kiraStore.installed||{};el.innerHTML=items.map(x=>{const yes=(st[kind]||[]).includes(x.id);const active=kind==='voices'?String(st.active_voice||'').includes(x.id):st.active_ai===x.id;return '<div class="catalogItem" data-search="'+(x.name+' '+(x.note||'')+' '+(x.category||'')).toLowerCase()+'"><h3>'+x.name+'</h3><small>'+(x.lang||x.note||x.kind||'')+'</small><div class="catalog-meta">'+meta(x)+'</div><div class="actions">'+(kind==='voices'?'<button onclick="previewVoice(\''+x.id+'\')">▶ Послушать</button>':'')+(yes?'<button '+(active?'disabled':'')+' onclick="useCatalog(\''+kind+'\',\''+x.id+'\')">'+(active?'★ Используется':'Использовать')+'</button><button onclick="removeCatalog(\''+kind+'\',\''+x.id+'\')">🗑</button>':'<button onclick="installCatalog(\''+kind+'\',\''+x.id+'\',this)">⬇ Установить</button>')+'</div></div>'}).join('')}
function storeSearch(inp,target){const q=inp.value.trim().toLowerCase();document.querySelectorAll('#'+target+' .catalogItem').forEach(c=>c.style.display=(c.dataset.search||'').includes(q)?'':'none')}
async function installCatalog(kind,id,b){
 b.disabled=true;b.textContent='⏳ В очередь…';
 try{
  const r=await fetch('/catalog/'+kind+'/'+encodeURIComponent(id)+'/install',{method:'POST'});if(!r.ok)throw Error(await r.text());
  const job=await r.json();showDownloadManager();await watchStoreJob(job.id,b);
 }catch(e){b.disabled=false;b.textContent='↻ Повторить'}
}
async function watchStoreJob(id,b){
 for(;;){const r=await fetch('/catalog/jobs/'+id,{cache:'no-store'});if(!r.ok)break;const j=await r.json();renderDownloadJob(j);
  if(j.status==='done'){b.textContent='✓ Готово';await loadCatalog();return}
  if(j.status==='error'){b.disabled=false;b.textContent='↻ Повторить';return}
  await new Promise(x=>setTimeout(x,700));
 }
}
function showDownloadManager(){let el=document.getElementById('kiraDownloads');if(!el){el=document.createElement('div');el.id='kiraDownloads';el.className='store-downloads';el.innerHTML='<div class="downloads-head"><b>⬇ Загрузки</b><button onclick="this.closest(\'.store-downloads\').classList.toggle(\'collapsed\')">⌄</button></div><div id="kiraDownloadJobs"></div>';document.body.appendChild(el)}return el}
function renderDownloadJob(j){showDownloadManager();const root=document.getElementById('kiraDownloadJobs');let row=document.getElementById('job-'+j.id);if(!row){row=document.createElement('div');row.id='job-'+j.id;row.className='download-job';root.prepend(row)}const p=Math.max(0,Math.min(100,j.progress||0)),fmt=n=>{if(!n)return '';const u=['B','KB','MB','GB'];let i=0;while(n>=1024&&i<3){n/=1024;i++}return n.toFixed(i?1:0)+' '+u[i]},meta=j.bytes_total?fmt(j.bytes_done)+' / '+fmt(j.bytes_total)+(j.speed_bps?' · '+fmt(j.speed_bps)+'/s':''):(j.message||'');
 row.innerHTML='<div><b>'+j.item_id+'</b><small>'+p+'% · '+j.status+'</small></div><div class="download-bar"><i style="width:'+p+'%"></i></div>'+(meta?'<small>'+meta+'</small>':'')+(j.error?'<small class="download-error">'+j.error+'</small>':'')}
}
async function restoreDownloads(){try{const d=await (await fetch('/catalog/jobs',{cache:'no-store'})).json();if(d.jobs&&d.jobs.length){showDownloadManager();d.jobs.slice(-8).forEach(renderDownloadJob)}}catch(e){}}
window.addEventListener('load',restoreDownloads);

function previewVoice(id){new Audio('/catalog/voices/'+encodeURIComponent(id)+'/preview?t='+Date.now()).play().catch(console.error)}
async function useCatalog(kind,id){const r=await fetch('/catalog/'+kind+'/'+encodeURIComponent(id)+'/use',{method:'POST'});if(r.ok)loadCatalog()}
async function removeCatalog(kind,id){if(!confirm('Удалить '+id+'?'))return;const r=await fetch('/catalog/'+kind+'/'+encodeURIComponent(id),{method:'DELETE'});if(r.ok)loadCatalog()}
window.addEventListener('load',loadCatalog);

function enhanceKiraStore(){
 [['voiceCatalog','voices','voiceCatalogList','голосов'],['aiCatalog','ai','aiCatalogList','моделей'],['pluginCatalog','plugins','pluginCatalogList','плагинов']].forEach(d=>{
  const root=document.getElementById(d[0]);if(!root||root.querySelector('.kira-store-toolbar'))return;
  const bar=document.createElement('div');bar.className='kira-store-toolbar';
  const all=document.createElement('button'),mine=document.createElement('button'),search=document.createElement('input'),count=document.createElement('span');
  all.textContent='Все';all.className='active';mine.textContent='Установленные';search.placeholder='🔎 Поиск…';count.className='store-count';
  const apply=mode=>{const q=search.value.trim().toLowerCase(),st=kiraStore.installed||{};document.querySelectorAll('#'+d[2]+' .catalogItem').forEach(c=>{const id=c.getAttribute('data-id')||'',okMode=mode==='all'||(st[d[1]]||[]).includes(id),okSearch=!q||c.innerText.toLowerCase().includes(q);c.style.display=okMode&&okSearch?'':'none'});all.classList.toggle('active',mode==='all');mine.classList.toggle('active',mode==='installed')};
  all.onclick=()=>apply('all');mine.onclick=()=>apply('installed');search.oninput=()=>apply(all.classList.contains('active')?'all':'installed');count.textContent=((kiraStore.installed||{})[d[1]]||[]).length+' '+d[3]+' установлено';
  bar.append(all,mine,search,count);root.insertBefore(bar,document.getElementById(d[2]));
 });
}
const kiraStoreLoadBase=loadCatalog;
loadCatalog=async function(){await kiraStoreLoadBase();document.querySelectorAll('.kira-store-toolbar').forEach(x=>x.remove());document.querySelectorAll('.catalogItem').forEach(c=>{const title=c.querySelector('h3');if(title){const groups=kiraStore.catalog||{};for(const kind of ['voices','ai','plugins']){const item=(groups[kind]||[]).find(i=>i.name===title.textContent);if(item){c.setAttribute('data-id',item.id);break}}}});enhanceKiraStore()}

function storeItem(kind,id){return ((kiraStore.catalog||{})[kind]||[]).find(x=>x.id===id)}
function openStoreDetail(kind,id){
 const x=storeItem(kind,id);if(!x)return;let modal=document.getElementById('kiraStoreDetail');
 if(!modal){modal=document.createElement('div');modal.id='kiraStoreDetail';modal.className='store-modal';document.body.appendChild(modal)}
 const st=kiraStore.installed||{},yes=(st[kind]||[]).includes(id),active=kind==='voices'?String(st.active_voice||'').includes(id):st.active_ai===id;
 const tags=[x.lang,x.engine,x.category,x.style,x.size_mb?'≈ '+x.size_mb+' MB':'',x.ram_gb?'RAM '+x.ram_gb+' GB':'',x.speed?'⚡ '+x.speed:'',x.quality?'✦ '+x.quality:''].filter(Boolean).map(v=>'<span>'+v+'</span>').join('');
 modal.innerHTML='<div class="store-detail"><button class="store-close" onclick="closeStoreDetail()">✕</button><div class="store-detail-icon">'+(kind==='voices'?'🎙':kind==='ai'?'🧠':'🧩')+'</div><h2>'+x.name+'</h2><p>'+(x.note||'Компонент Kira Studio')+'</p><div class="catalog-meta">'+tags+'</div><div class="store-detail-actions">'+(kind==='voices'?'<button onclick="previewVoice(\''+id+'\')">▶ Послушать</button>':'')+(yes?'<button '+(active?'disabled':'')+' onclick="useCatalog(\''+kind+'\',\''+id+'\').then(()=>openStoreDetail(\''+kind+'\',\''+id+'\'))">'+(active?'★ Используется':'Использовать')+'</button><button onclick="removeCatalog(\''+kind+'\',\''+id+'\').then(closeStoreDetail)">🗑 Удалить</button>':'<button onclick="detailInstall(\''+kind+'\',\''+id+'\',this)">⬇ Установить</button>')+'</div></div>';modal.classList.add('open')
}
function closeStoreDetail(){document.getElementById('kiraStoreDetail')?.classList.remove('open')}
async function detailInstall(kind,id,b){await installCatalog(kind,id,b);setTimeout(()=>openStoreDetail(kind,id),500)}
document.addEventListener('click',e=>{const card=e.target.closest('.catalogItem');if(!card||e.target.closest('button'))return;const id=card.getAttribute('data-id');if(!id)return;let kind=card.closest('#voiceCatalogList')?'voices':card.closest('#aiCatalogList')?'ai':card.closest('#pluginCatalogList')?'plugins':'';if(kind)openStoreDetail(kind,id)})
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeStoreDetail()})
