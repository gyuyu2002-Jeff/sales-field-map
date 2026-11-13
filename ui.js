function updateRegionLabel() {
  const county=COUNTIES[currentCounty]?.name || '全台';
  const park=PARKS[currentPark]?.name || '全部園區';
  document.getElementById('regionLabel').textContent=county+' › '+park;
}
function openRegionPicker() {
  const county=document.getElementById('regionCounty');
  county.replaceChildren(new Option('全台','all'),...Object.entries(COUNTIES).map(([id,c])=>new Option(c.name,id)));
  county.value=currentCounty;
  populateRegionParks();
  document.getElementById('regionPark').value=currentPark;
  document.getElementById('regionSearch').value='';
  document.getElementById('regionResults').replaceChildren();
  document.getElementById('modalRegion').classList.add('open');
}
function populateRegionParks() {
  const cid=document.getElementById('regionCounty').value;
  const ids=cid==='all'?Object.keys(PARKS):COUNTIES[cid].parks;
  document.getElementById('regionPark').replaceChildren(new Option('全部園區',cid==='all'?'all_taiwan':'all_'+cid),...ids.map(pid=>new Option(PARKS[pid].name,pid)));
}
function chooseRegion(cid,pid) {
  currentCounty=cid;
  document.getElementById('modalRegion').classList.remove('open');
  switchPark(pid);
}
let selectedMapClientId=null;
function refreshMapClient() {
  if(document.getElementById('mapClientPanel').hidden)return;
  const client=currentFiltered.find(c=>c.id===selectedMapClientId);
  if(client)showMapClient(client);
  else document.getElementById('mapClientPanel').hidden=true;
}
function showMapClient(client) {
  if(innerWidth>768 || currentMobileView!=='map')return;
  selectedMapClientId=client.id;
  const card=createClientCard(client);
  card.removeAttribute('id');card.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));
  document.getElementById('mapClientContent').replaceChildren(card);
  document.getElementById('mapClientPanel').hidden=false;
}
document.addEventListener('DOMContentLoaded',()=>{
  const menu=document.getElementById('moreTools');
  menu.addEventListener('click',e=>{if(e.target.closest('button')){menu.open=false;menu.querySelector('summary').focus();}});
  document.addEventListener('click',e=>{if(!menu.contains(e.target))menu.open=false;});
  menu.addEventListener('keydown',e=>{if(e.key==='Escape'){menu.open=false;menu.querySelector('summary').focus();}});
  document.getElementById('regionCounty').onchange=populateRegionParks;
  document.getElementById('regionApply').onclick=()=>chooseRegion(document.getElementById('regionCounty').value,document.getElementById('regionPark').value);
  const regionSearch=document.getElementById('regionSearch');
  let regionComposing=false;
  regionSearch.addEventListener('compositionstart',()=>{regionComposing=true;});
  regionSearch.addEventListener('compositionend',e=>{regionComposing=false;renderRegionSearch(e.target.value);});
  function renderRegionSearch(rawValue) {
    const norm=SalesData.normalizeSearchText ? SalesData.normalizeSearchText(rawValue) : String(rawValue || '').trim().toLowerCase().replace(/臺/g,'台');
    const tokens=norm ? norm.split(/\s+/).filter(Boolean) : [];
    const results=document.getElementById('regionResults');results.replaceChildren();
    if(!tokens.length)return;
    const matches=[];
    for(const [cid,c] of Object.entries(COUNTIES)) {
      const countyNorm=SalesData.normalizeSearchText ? SalesData.normalizeSearchText(`${c.name} ${c.region || ''} 全部園區 總覽`) : `${c.name} 全部園區 總覽`.toLowerCase().replace(/臺/g,'台');
      if(tokens.every(t=>countyNorm.includes(t))) {
        const total=(c.parks || []).reduce((s,pid)=>s+(PARKS[pid]?.count || 0),0);
        matches.push({cid,pid:'all_'+cid,label:`${c.name} › 全部園區總覽 (${(c.parks || []).length} 園區 · ${total.toLocaleString()} 家)`});
      }
    }
    for(const [pid,p] of Object.entries(PARKS)) {
      const cName=COUNTIES[p.county_id]?.name || '';
      const parkNorm=SalesData.normalizeSearchText ? SalesData.normalizeSearchText(`${cName} ${p.name} ${pid}`) : `${cName} ${p.name}`.toLowerCase().replace(/臺/g,'台');
      if(tokens.every(t=>parkNorm.includes(t))) {
        matches.push({cid:p.county_id,pid,label:`${cName} › ${p.name} (${(p.count || 0).toLocaleString()} 家)`});
      }
    }
    for(const item of matches) {
      const button=document.createElement('button');button.type='button';button.textContent=item.label;
      button.onclick=()=>chooseRegion(item.cid,item.pid);results.append(button);
    }
    if(!results.childElementCount)results.textContent='找不到符合的園區，請試試縣市或園區名稱。';
  }
  regionSearch.oninput=e=>{if(!regionComposing)renderRegionSearch(e.target.value);};
  regionSearch.addEventListener('keydown',e=>{
    const buttons=[...document.querySelectorAll('#regionResults button')];
    if(e.key==='Enter' && buttons.length){e.preventDefault();buttons[0].click();}
    else if(e.key==='ArrowDown' && buttons.length){e.preventDefault();buttons[0].focus();}
  });
  document.getElementById('regionResults').addEventListener('keydown',e=>{
    const buttons=[...document.querySelectorAll('#regionResults button')];
    const idx=buttons.indexOf(document.activeElement);
    if(idx<0)return;
    if(e.key==='ArrowDown'){e.preventDefault();(buttons[idx+1] || buttons[0]).focus();}
    else if(e.key==='ArrowUp'){e.preventDefault();if(idx===0)regionSearch.focus();else buttons[idx-1].focus();}
  });
});
