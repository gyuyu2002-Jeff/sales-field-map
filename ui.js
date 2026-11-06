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
  document.getElementById('regionSearch').oninput=e=>{
    const q=e.target.value.trim();const results=document.getElementById('regionResults');results.replaceChildren();
    if(!q)return;
    for(const [pid,p] of Object.entries(PARKS).filter(([id,p])=>(COUNTIES[p.county_id].name+p.name).includes(q))) {
      const button=document.createElement('button');button.type='button';button.textContent=COUNTIES[p.county_id].name+' › '+p.name;
      button.onclick=()=>chooseRegion(p.county_id,pid);results.append(button);
    }
    if(!results.childElementCount)results.textContent='找不到符合的園區，請試試縣市或園區名稱。';
  };
});
