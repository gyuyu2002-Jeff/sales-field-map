const {escapeHtml, validCoordinates, normalizeClient, mergeClients, parseCSV, csvCell} = SalesData;
const STORE_KEY = 'sales_field_map_v3';
const BACKUP_TIME_KEY = 'sales_field_map_last_backup';
const preferenceKeys = ['sales_custom_stages_v2','sales_map_default_county','sales_map_default_county_prompted'];
let pendingImport = null;
let parkLoadSequence = 0;
const parkLoads = new Map();

function readStore() {
  const raw = localStorage.getItem(STORE_KEY);
  if (raw) {
    const store = JSON.parse(raw);
    if (store.version !== 1 || !store.parks || !store.settings) throw Error('本機資料格式不正確，請先備份原始資料');
    return store;
  }
  const store = {version:1, parks:{}, settings:{}};
  for (const [pid, park] of Object.entries(PARKS)) {
    const saved = localStorage.getItem(getParkStorageKey(pid));
    if (saved) store.parks[pid] = {mode:'merge', clients:JSON.parse(saved).map(c=>normalizeClient(c,pid,park.county_id))};
  }
  for (const key of preferenceKeys) {
    const value = localStorage.getItem(key);
    if (value !== null) store.settings[key] = value;
  }
  return store;
}

const appStorage = {
  getItem(key) { try { return readStore().settings[key] ?? null; } catch(e) { return localStorage.getItem(key); } },
  setItem(key,value) { const store=readStore(); store.settings[key]=String(value); localStorage.setItem(STORE_KEY,JSON.stringify(store)); }
};

function storageFailure(e) {
  alert('未儲存成功：'+e.message+'。請立即下載完整備份；清除瀏覽器資料前務必備份。');
}

function getPersistedParkClients(pid) {
  const park=PARKS[pid];
  const saved=readStore().parks[pid];
  if(saved?.mode==='replace') return saved.clients.map(c=>normalizeClient(c,pid,park.county_id));
  return mergeClients(park.clients || [],saved?.clients || [],pid,park.county_id);
}

function currentParkIds(id=currentPark) {
  if(id==='all_taiwan') return Object.keys(PARKS);
  if(id.startsWith('all_')) return COUNTIES[id.slice(4)].parks;
  return [id];
}

function nextClientId() {
  let next=Date.now();
  for(const entry of Object.values(readStore().parks)) {
    for(const c of entry.clients) next=Math.max(next,c.id+1);
  }
  for(const c of clients) next=Math.max(next,c.id+1);
  return next;
}

function saveCurrentParkData() {
  try {
    const store=readStore();
    for(const pid of currentParkIds()) {
      const mode=store.parks[pid]?.mode || 'merge';
      const base=new Map((PARKS[pid].clients || []).map(c=>[c.id,c]));
      const rows=clients.filter(c=>c.park_id===pid).map(c=>normalizeClient(c,pid,PARKS[pid].county_id));
      // Save only local changes; an overview edit must not duplicate the national catalog.
      const changes=mode==='replace'?rows:rows.filter(c=>{
        const original=base.get(c.id);
        return !original || c.status!==original.status || c.notes!==original.notes || JSON.stringify(c.visit_logs)!==JSON.stringify(original.visit_logs);
      });
      store.parks[pid]={mode, clients:changes};
    }
    localStorage.setItem(STORE_KEY,JSON.stringify(store));
    return true;
  } catch(e) {
    storageFailure(e);
    try { clients=currentParkIds().flatMap(getPersistedParkClients); renderList(); } catch {}
    return false;
  }
}

async function ensureParkData(id) {
  await Promise.all(currentParkIds(id).map(pid=>{
    if(PARKS[pid].clients) return;
    if(!parkLoads.has(pid)) {
      parkLoads.set(pid, fetch(PARKS[pid].data_url).then(r=>{
        if(!r.ok) throw Error('園區資料載入失敗，請稍後重試');
        return r.json();
      }).then(rows=>{PARKS[pid].clients=rows.map(c=>normalizeClient(c,pid,PARKS[pid].county_id));})
        .catch(e=>{parkLoads.delete(pid);throw e;}));
    }
    return parkLoads.get(pid);
  }));
}

function downloadFile(name, content, type) {
  const url=URL.createObjectURL(new Blob([content],{type}));
  const a=document.createElement('a'); a.href=url; a.download=name; a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function backupAll() {
  try {
    const snapshot={format:'sales-field-map',...readStore(),exported_at:new Date().toISOString()};
    downloadFile('巡訪完整備份_'+Date.now()+'.json',JSON.stringify(snapshot,null,2),'application/json');
    localStorage.setItem(BACKUP_TIME_KEY,new Date().toISOString());
    updateStorageNotice();
    return true;
  } catch(e) { storageFailure(e); return false; }
}

function updateStorageNotice() {
  const date=localStorage.getItem(BACKUP_TIME_KEY);
  document.getElementById('storageNotice').textContent='僅存此裝置，未跨裝置同步 · '+(date?'最近下載備份：'+new Date(date).toLocaleString('zh-TW'):'尚未下載備份');
}

function validateBackup(value) {
  if(value.format!=='sales-field-map' || value.version!==1 || !value.parks || !value.settings) throw Error('不是支援的巡訪備份檔');
  const store={version:1,parks:{},settings:{}};
  for(const [pid,entry] of Object.entries(value.parks)) {
    if(!Object.hasOwn(PARKS,pid) || !['merge','replace'].includes(entry.mode) || !Array.isArray(entry.clients)) throw Error('備份園區或名單格式錯誤');
    const rows=entry.clients.map(c=>normalizeClient(c,pid,PARKS[pid].county_id));
    if(new Set(rows.map(c=>c.id)).size!==rows.length) throw Error('備份有重複客戶編號');
    store.parks[pid]={mode:entry.mode,clients:rows};
  }
  for(const key of preferenceKeys) if(Object.hasOwn(value.settings,key)) {
    if(typeof value.settings[key]!=='string') throw Error('備份設定格式錯誤');
    store.settings[key]=value.settings[key];
  }
  const stages=store.settings.sales_custom_stages_v2;
  if(stages && (!Array.isArray(JSON.parse(stages)) || JSON.parse(stages).some(s=>typeof s!=='string'))) throw Error('洽談階段格式錯誤');
  return store;
}

function parseAndImportCSV(csvText) {
  if(!PARKS[currentPark]) throw Error('請先選擇單一園區，再匯入名單');
  const rows=parseCSV(csvText);
  if(rows.length<2) throw Error('CSV 沒有客戶資料');
  const headers=rows.shift().map(h=>h.trim());
  const col=(row,...keys)=>{const i=headers.findIndex(h=>keys.includes(h));return i<0?'':row[i] || '';};
  if(!headers.includes('公司名稱') && !headers.includes('name')) throw Error('CSV 必須包含「公司名稱」欄位');
  const start=nextClientId();
  const imported=rows.map((row,i)=>{
    if(row.length!==headers.length) throw Error('第 '+(i+2)+' 筆欄位數不符');
    const latText=col(row,'緯度(Lat)','lat'),lngText=col(row,'經度(Lng)','lng');
    const coords={lat:latText.trim()?Number(latText):null,lng:lngText.trim()?Number(lngText):null};
    if((latText || lngText) && !validCoordinates(coords)) throw Error('第 '+(i+2)+' 筆經緯度無效');
    const c={id:start+i, name:col(row,'公司名稱','name'),road:col(row,'所在路段','road'),address:col(row,'完整廠址','address'),...coords,
      industry:col(row,'產業類別','industry'),is_listed:col(row,'是否上市櫃','is_listed'),status:col(row,'拜訪狀態','status'),
      contact:col(row,'聯絡窗口','contact'),phone:col(row,'聯絡電話','phone'),notes:col(row,'拜訪備忘與筆記','notes'),visit_logs:[]};
    const summary=col(row,'最新洽談重點');
    if(summary) c.visit_logs=[{id:'v_'+(start+i),date:col(row,'最新拜訪日期'),contact:col(row,'最新接洽對象'),outcome:col(row,'最新洽談階段'),summary,next_action:col(row,'下次預計待辦事項與回訪日')}];
    return normalizeClient(c,currentPark,currentCounty);
  });
  pendingImport={type:'csv',pid:currentPark,rows:imported};
  document.getElementById('importSummary').textContent=`解析成功 ${imported.length} 筆，${imported.filter(c=>!validCoordinates(c)).length} 筆待定位。CSV 僅有最新拜訪摘要，完整還原請使用 JSON 備份。\n前 3 筆：${imported.slice(0,3).map(c=>c.name).join('、')}`;
  document.getElementById('importAppend').hidden=false;
  document.getElementById('importReplace').textContent='備份後覆蓋本園區';
  document.getElementById('modalImport').classList.add('open');
}

function finishImport(replace) {
  if(!pendingImport) return;
  try {
    if(replace && !backupAll()) return;
    let store;
    if(pendingImport.type==='backup') store=pendingImport.store;
    else {
      store=readStore();
      const {pid,rows}=pendingImport;
      store.parks[pid]={mode:replace?'replace':store.parks[pid]?.mode || 'merge',clients:replace?rows:[...getPersistedParkClients(pid),...rows]};
    }
    localStorage.setItem(STORE_KEY,JSON.stringify(store));
    pendingImport=null;
    document.getElementById('modalImport').classList.remove('open');
    loadCustomStages(); populateStageOptions(); loadParkData(currentPark);
    updateStorageNotice(); showToast('資料已儲存於此裝置');
  } catch(e) { storageFailure(e); }
}

document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('btnBackup').onclick=backupAll;
  document.getElementById('importAppend').onclick=()=>finishImport(false);
  document.getElementById('importReplace').onclick=()=>finishImport(true);
  document.getElementById('importCancel').onclick=()=>{pendingImport=null;document.getElementById('modalImport').classList.remove('open');};
  const fileInput=document.getElementById('fileInput');
  fileInput.addEventListener('change',async e=>{
    const file=e.target.files[0]; if(!file)return;
    try {
      if(file.size>20*1024*1024) throw Error('檔案超過 20 MB，請拆分名單');
      const content=await file.text();
      if(file.name.toLowerCase().endsWith('.json')) {
        const store=validateBackup(JSON.parse(content));
        pendingImport={type:'backup',store};
        document.getElementById('importSummary').textContent=`將還原 ${Object.keys(store.parks).length} 個園區的客戶與全部拜訪紀錄。還原會取代目前本機資料，會先下載現有備份。`;
        document.getElementById('importAppend').hidden=true;
        document.getElementById('importReplace').textContent='備份後完整還原';
        document.getElementById('modalImport').classList.add('open');
      } else parseAndImportCSV(content);
    } catch(e) {alert('匯入未執行：'+e.message);} finally {fileInput.value='';}
  });
  updateStorageNotice();
  // Modal semantics, focus trapping and Escape, including dialogs opened by existing controls.
  for(const modal of document.querySelectorAll('.modal-overlay')) {
    modal.setAttribute('role','dialog'); modal.setAttribute('aria-modal','true');
    modal.setAttribute('aria-label',modal.querySelector('h3,h2')?.textContent || '巡訪設定');
    modal.tabIndex=-1;
    let opener=null,wasOpen=false;
    const focusables=()=>[...modal.querySelectorAll('button,input,textarea,select,a[href]')].filter(e=>e.getClientRects().length&&!e.disabled);
    new MutationObserver(()=>{
      const open=modal.classList.contains('open');
      if(open&&!wasOpen){opener=document.activeElement;(focusables()[0] || modal).focus();}
      if(!open&&wasOpen)opener?.focus();
      wasOpen=open;
    }).observe(modal,{attributes:true,attributeFilter:['class']});
    modal.addEventListener('keydown',e=>{
      if(e.key==='Escape'){modal.classList.remove('open');e.stopPropagation();}
      if(e.key==='Tab'){
        const items=focusables(),first=items[0],last=items.at(-1);
        if(!first){e.preventDefault();return;}
        if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
        else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
      }
    });
  }
  for(const label of document.querySelectorAll('.form-group label')) {
    const input=label.parentElement.querySelector('input,select,textarea');if(input?.id)label.htmlFor=input.id;
  }
});
