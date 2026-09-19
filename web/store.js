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
 row.innerHTML='<div><b>'+j.item_id+'</b><small>'+p+'% · '+j.status+'</small></div><div class="download-bar"><i style="width:'+p+'%"></i></div>'+(meta?'<small>'+meta+'</small>':'')+(j.error?'<small class="download-error">'+j.error+'</small>':'')+(['queued','installing','cancelling'].includes(j.status)?'<button class="download-cancel" onclick="cancelStoreJob(\''+j.id+'\')">Отмена</button>':'')}
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

async function cancelStoreJob(id){try{await fetch('/catalog/jobs/'+id+'/cancel',{method:'POST'});const r=await fetch('/catalog/jobs/'+id,{cache:'no-store'});if(r.ok)renderDownloadJob(await r.json())}catch(e){}}

function storePlatformNotice(){
 const p=typeof kiraPlatform==='function'?kiraPlatform():'Kira Studio';
 document.querySelectorAll('#voiceCatalog,#aiCatalog,#pluginCatalog').forEach((root,i)=>{
  if(root.querySelector('.store-platform-note'))return;
  const n=document.createElement('div');n.className='store-platform-note';
  n.innerHTML='<b>'+p+'</b><span>'+(p==='Android'?'Компоненты устанавливаются на подключённый Kira Core.':'Компоненты устанавливаются локально в Kira Studio.')+'</span>';
  root.prepend(n);
 });
}
window.addEventListener('load',storePlatformNotice);

function kiraPlatform(){
 if(window.KiraAndroid)return {id:'android',icon:'📱',name:'Android'};
 const p=(navigator.userAgentData?.platform||navigator.platform||'').toLowerCase();
 if(p.includes('win'))return {id:'windows',icon:'🪟',name:'Windows'};
 if(p.includes('linux'))return {id:'linux',icon:'🐧',name:'Linux / Arch'};
 return {id:'web',icon:'🌐',name:'Web'};
}
function ensureAppShell(){
 if(document.getElementById('kiraAppShell'))return;
 const p=kiraPlatform(),shell=document.createElement('div');shell.id='kiraAppShell';shell.className='kira-app-shell';
 shell.innerHTML='<div class="app-platform">'+p.icon+' <b>Kira Studio</b><span>'+p.name+'</span></div><div class="app-quick"><button id="appCore">● Core</button><button onclick="document.getElementById(\'voiceCatalog\')?.scrollIntoView({behavior:\'smooth\'})">🛍 Store</button><button onclick="showDownloadManager()">⬇ Загрузки</button></div>';
 document.body.prepend(shell);refreshAppShell();
}
async function refreshAppShell(){const b=document.getElementById('appCore');if(!b)return;try{const r=await fetch('/health',{cache:'no-store'});b.classList.toggle('online',r.ok);b.textContent=r.ok?'● Core онлайн':'● Core ошибка'}catch(e){b.classList.remove('online');b.textContent='● Core офлайн'}}
window.addEventListener('load',()=>{ensureAppShell();setInterval(refreshAppShell,10000)});

function firstRunWizard(){
 if(localStorage.getItem('kiraAppSetupV2'))return;
 const p=kiraPlatform(),m=document.createElement('div');m.id='kiraFirstRun';m.className='store-modal open';
 m.innerHTML='<div class="store-detail setup-card"><div class="setup-kicker">'+p.icon+' '+p.name+'</div><h2>Добро пожаловать в Kira Studio</h2><p>Быстрая проверка приложения перед первым запуском.</p><div id="setupChecks" class="setup-checks"></div><div class="store-detail-actions"><button id="setupCheck">Проверить систему</button><button id="setupFinish" disabled>Продолжить</button></div></div>';
 document.body.appendChild(m);
 document.getElementById('setupCheck').onclick=runFirstRunChecks;
 document.getElementById('setupFinish').onclick=()=>{localStorage.setItem('kiraAppSetupV2','1');m.remove()};
}
async function runFirstRunChecks(){
 const p=kiraPlatform(),box=document.getElementById('setupChecks'),finish=document.getElementById('setupFinish');box.innerHTML='';finish.disabled=true;
 const checks=[['Kira Core','/health'],['Store','/catalog'],['Live2D','/live2d/status']];
 if(p.id!=='android')checks.push(['Диагностика','/diagnostics']);
 let required=true;
 for(const [name,url] of checks){const row=document.createElement('div');row.className='setup-row';row.innerHTML='<span>'+name+'</span><b>проверка…</b>';box.appendChild(row);try{const r=await fetch(url,{cache:'no-store'});row.classList.add(r.ok?'ok':'bad');row.querySelector('b').textContent=r.ok?'✓ готово':'✕ ошибка';if(name==='Kira Core'&&!r.ok)required=false}catch(e){row.classList.add('bad');row.querySelector('b').textContent='✕ недоступно';if(name==='Kira Core')required=false}}
 finish.disabled=!required;
}
window.addEventListener('load',()=>setTimeout(firstRunWizard,250));

function openInstalledLibrary(){
 let m=document.getElementById('kiraLibrary');if(!m){m=document.createElement('div');m.id='kiraLibrary';m.className='store-modal';document.body.appendChild(m)}
 const st=kiraStore.installed||{},groups=[['voices','🎙 Голоса'],['ai','🧠 ИИ-модели'],['plugins','🧩 Плагины']];
 let body=groups.map(([k,t])=>{const ids=st[k]||[];return '<section class="library-group"><h3>'+t+' <small>'+ids.length+'</small></h3>'+(ids.length?ids.map(id=>{const x=storeItem(k,id)||{id,name:id};const active=k==='voices'?String(st.active_voice||'').includes(id):k==='ai'?st.active_ai===id:false;return '<div class="library-row"><div><b>'+x.name+'</b><small>'+id+'</small></div><span>'+(active?'★ Активен':'✓ Установлен')+'</span><button onclick="openStoreDetail(\''+k+'\',\''+id+'\')">Открыть</button></div>'}).join(''):'<p class="library-empty">Пока ничего не установлено</p>')+'</section>'}).join('');
 m.innerHTML='<div class="store-detail library-card"><button class="store-close" onclick="closeInstalledLibrary()">✕</button><div class="store-detail-icon">📚</div><h2>Моя библиотека</h2><p>Все локальные компоненты Kira Studio на этом устройстве.</p>'+body+'</div>';m.classList.add('open')
}
function closeInstalledLibrary(){document.getElementById('kiraLibrary')?.classList.remove('open')}
function addLibraryShortcut(){const q=document.querySelector('.app-quick');if(q&&!document.getElementById('libraryShortcut')){const b=document.createElement('button');b.id='libraryShortcut';b.textContent='📚 Библиотека';b.onclick=openInstalledLibrary;q.insertBefore(b,q.lastElementChild)}}
window.addEventListener('load',()=>setTimeout(addLibraryShortcut,100));

async function loadVoiceEngines(){
 try{const r=await fetch('/catalog/engines',{cache:'no-store'}),d=await r.json();renderVoiceEngines(d.engines||[])}catch(e){}
}
function renderVoiceEngines(items){
 let host=document.getElementById('voiceEngineCatalog');
 if(!host){const v=document.getElementById('voiceCatalog');if(!v)return;host=document.createElement('div');host.id='voiceEngineCatalog';host.className='engine-catalog';v.parentNode.insertBefore(host,v)}
 host.innerHTML='<div class="engine-head"><div><b>⚙️ Движки голосов</b><small>Скачивай только нужные. Удалённые движки остаются в каталоге.</small></div></div><div class="engine-grid">'+items.map(x=>'<article class="engine-card '+(x.installed?'installed':'')+'"><div><b>'+x.name+'</b><small>'+x.description+'</small></div><span>'+(x.installed?'✓ Установлен':'Не установлен')+'</span><button onclick="toggleVoiceEngine(\''+x.id+'\','+(!x.installed)+',this)">'+(x.installed?'Удалить':'Скачать')+'</button></article>').join('')+'</div>';
}
async function toggleVoiceEngine(id,install,b){
 const old=b.textContent;b.disabled=true;b.textContent=install?'Установка…':'Удаление…';
 try{const r=await fetch('/catalog/engines/'+encodeURIComponent(id)+(install?'/install':''),{method:install?'POST':'DELETE'});if(!r.ok)throw new Error(await r.text());await loadVoiceEngines();await loadCatalog()}
 catch(e){b.disabled=false;b.textContent=old;alert('Kira Store: '+e.message)}
}
function engineForVoice(id){const x=(kiraStore.catalog?.voices||[]).find(v=>v.id===id);return x?.engine||'piper'}
const _openStoreDetailEngine=typeof openStoreDetail==='function'?openStoreDetail:null;
if(_openStoreDetailEngine)openStoreDetail=function(kind,id){_openStoreDetailEngine(kind,id);if(kind==='voices'){setTimeout(()=>{const x=(kiraStore.catalog?.voices||[]).find(v=>v.id===id);if(!x)return;const card=document.querySelector('#kiraStoreDetail .store-detail');if(!card)return;const tag=document.createElement('div');tag.className='voice-engine-tag';tag.textContent='⚙️ Движок: '+(x.engine||'piper');const actions=card.querySelector('.store-detail-actions');card.insertBefore(tag,actions||null)},0)}};
window.addEventListener('load',()=>setTimeout(loadVoiceEngines,350));


async function openCharacterOptimizer(){
 let m=document.getElementById('characterOptimizer');if(!m){m=document.createElement('div');m.id='characterOptimizer';m.className='store-modal';document.body.appendChild(m)}
 m.innerHTML='<div class="store-detail character-optimizer"><button class="store-close" onclick="closeCharacterOptimizer()">✕</button><div class="store-detail-icon">🦊</div><h2>Оптимизация персонажа</h2><p>ИИ, голос и анимация настраиваются под активную Live2D-модель.</p><div id="characterOptimizerBody">Анализ модели…</div><div class="store-detail-actions"><button onclick="fullCharacterCalibration(this)">⚡ Полная калибровка</button><button onclick="autoTuneCharacter(this)">✨ Автонастройка</button><button onclick="calibrateCharacterVoice(this)">🎙 Калибровать голос</button><button onclick="calibrateCharacterAI(this)">🧠 Калибровать ИИ</button></div></div>';m.classList.add('open');
 try{const r=await fetch('/character/profile',{cache:'no-store'}),d=await r.json();renderCharacterOptimizer(d)}catch(e){document.getElementById('characterOptimizerBody').textContent='Не удалось получить профиль: '+e.message}
}
function closeCharacterOptimizer(){document.getElementById('characterOptimizer')?.classList.remove('open')}
function renderCharacterOptimizer(d){
 const b=document.getElementById('characterOptimizerBody');if(!b)return;const c=d.capabilities||{},p=d.profile||{},v=p.voice||{},ai=p.ai||{},motion=p.motion||{};
 const parts=Object.entries(c).map(([k,on])=>'<span class="'+(on?'cap-on':'cap-off')+'">'+(on?'✓ ':'✕ ')+k+'</span>').join('');
 b.innerHTML='<div class="character-caps">'+parts+'</div><div class="character-tune-grid"><div><b>🧠 ИИ</b><small>'+esc(ai.reply_style||'по умолчанию')+'</small><span>Temperature '+Number(ai.temperature??0.75).toFixed(2)+'</span></div><div><b>🎙 Голос</b><small>Скорость '+Number(v.speed??1).toFixed(2)+'×</small><span>Mouth gain '+Number(v.mouth_gain??1).toFixed(2)+'</span></div><div><b>🎭 Анимация</b><small>Уши '+Number(motion.ear_reactivity??0).toFixed(2)+'</small><span>Хвост '+Number(motion.tail_reactivity??0).toFixed(2)+'</span></div></div>';
}
async function autoTuneCharacter(b){const old=b.textContent;b.disabled=true;b.textContent='Анализ…';try{const r=await fetch('/character/auto-tune',{method:'POST'});if(!r.ok)throw Error(await r.text());renderCharacterOptimizer(await r.json());b.textContent='✓ Настроено'}catch(e){b.textContent=old;alert(e.message)}finally{setTimeout(()=>b.disabled=false,500)}}
async function calibrateCharacterVoice(b){const old=b.textContent;b.disabled=true;b.textContent='🎙 Говорю тестовую фразу…';try{const r=await fetch('/character/calibrate-voice',{method:'POST'});if(!r.ok)throw Error(await r.text());const d=await r.json();renderCharacterOptimizer(d);b.textContent='✓ Голос откалиброван'}catch(e){b.textContent=old;alert('Калибровка: '+e.message)}finally{setTimeout(()=>b.disabled=false,500)}}
function addCharacterOptimizerShortcut(){const q=document.querySelector('.app-quick');if(q&&!document.getElementById('characterOptimizerShortcut')){const b=document.createElement('button');b.id='characterOptimizerShortcut';b.textContent='🦊 Персонаж';b.onclick=openCharacterOptimizer;q.insertBefore(b,q.lastElementChild)}}
window.addEventListener('load',()=>setTimeout(addCharacterOptimizerShortcut,140));

async function calibrateCharacterAI(b){const old=b.textContent;b.disabled=true;b.textContent='🧠 Проверяю ответы…';try{const r=await fetch('/character/calibrate-ai',{method:'POST'});if(!r.ok)throw Error(await r.text());const d=await r.json();b.textContent='✓ ИИ '+d.score+'/100';const p=await fetch('/character/profile',{cache:'no-store'}).then(x=>x.json());renderCharacterOptimizer(p)}catch(e){b.textContent=old;alert('Калибровка ИИ: '+e.message)}finally{setTimeout(()=>b.disabled=false,700)}}

async function fullCharacterCalibration(b){const old=b.textContent;b.disabled=true;b.textContent='⚡ Калибрую персонажа…';try{const r=await fetch('/character/full-calibration',{method:'POST'});if(!r.ok)throw Error(await r.text());const d=await r.json();const p=d.profile||await fetch('/character/profile',{cache:'no-store'}).then(x=>x.json());renderCharacterOptimizer(p);let box=document.getElementById('characterCalibrationReport');if(!box){box=document.createElement('div');box.id='characterCalibrationReport';document.getElementById('characterOptimizerBody')?.appendChild(box)}box.className='calibration-report '+(d.ready?'ready':'warning');box.innerHTML='<b>'+(d.ready?'✓ Персонаж готов':'⚠ Требуется внимание')+'</b>'+d.steps.map(x=>'<div><span>'+(x.ok?'✓':'✕')+' '+x.id+'</span><small>'+(x.score!=null?'оценка '+x.score+'/100':x.error||'готово')+'</small></div>').join('');b.textContent=d.ready?'✓ Калибровка завершена':'⚠ Калибровка завершена'}catch(e){b.textContent=old;alert('Полная калибровка: '+e.message)}finally{setTimeout(()=>b.disabled=false,900)}}

function openVoiceCompare(){
 const voices=(kiraStore.catalog?.voices||[]).filter(x=>x.gender==='female');
 let m=document.getElementById('voiceCompare');if(!m){m=document.createElement('div');m.id='voiceCompare';m.className='store-modal';document.body.appendChild(m)}
 const opts=voices.map(x=>'<option value="'+x.id+'">'+esc(x.name)+'</option>').join('');
 m.innerHTML='<div class="store-detail voice-compare"><button class="store-close" onclick="closeVoiceCompare()">✕</button><div class="store-detail-icon">🎧</div><h2>A/B сравнение голосов</h2><p>Одна фраза, разные голоса. Прослушивание не меняет голос персонажа.</p><input id="voiceCompareText" maxlength="240" value="Привет! Я Кира. Давай проверим, какой голос подходит мне лучше."><div class="voice-compare-grid">'+[0,1,2,3].map((n)=>'<div><select id="voiceCompare'+n+'"><option value="">Голос '+(n+1)+'</option>'+opts+'</select><button onclick="playComparedVoice('+n+',this)">▶ Прослушать</button><button onclick="selectComparedVoice('+n+',this)">★ Выбрать</button></div>').join('')+'</div><small>Для прослушивания движок и голос должны быть доступны в Store.</small></div>';
 m.classList.add('open')
}
function closeVoiceCompare(){document.getElementById('voiceCompare')?.classList.remove('open')}
function comparedVoiceId(n){return document.getElementById('voiceCompare'+n)?.value||''}
async function playComparedVoice(n,b){
 const id=comparedVoiceId(n);if(!id)return;const text=document.getElementById('voiceCompareText')?.value.trim()||'Привет! Я Кира.';
 const old=b.textContent;b.disabled=true;b.textContent='⏳ Генерация…';
 try{const a=new Audio('/catalog/voices/'+encodeURIComponent(id)+'/preview?text='+encodeURIComponent(text)+'&t='+Date.now());await a.play();b.textContent='▶ Играет'}
 catch(e){b.textContent='⚠ Ошибка'}finally{setTimeout(()=>{b.disabled=false;b.textContent=old},1200)}
}
async function selectComparedVoice(n,b){
 const id=comparedVoiceId(n);if(!id)return;const st=kiraStore.installed||{};
 if(!(st.voices||[]).includes(id)){alert('Сначала установите или добавьте этот голос в Store.');return}
 const old=b.textContent;b.disabled=true;b.textContent='⏳ Выбираю…';
 try{const r=await fetch('/catalog/voices/'+encodeURIComponent(id)+'/use',{method:'POST'});if(!r.ok)throw Error(await r.text());await loadCatalog();b.textContent='★ Выбран'}
 catch(e){b.textContent='⚠ Ошибка'}finally{setTimeout(()=>{b.disabled=false;b.textContent=old},900)}
}
function addVoiceCompareShortcut(){
 const root=document.getElementById('voiceCatalog');if(!root||document.getElementById('voiceCompareBtn'))return;
 const b=document.createElement('button');b.id='voiceCompareBtn';b.textContent='🎧 Сравнить голоса';b.onclick=openVoiceCompare;
 const bar=root.querySelector('.kira-store-toolbar');if(bar)bar.appendChild(b);else root.prepend(b)
}
const voiceCompareLoad=loadCatalog;
loadCatalog=async function(){await voiceCompareLoad();addVoiceCompareShortcut()}
