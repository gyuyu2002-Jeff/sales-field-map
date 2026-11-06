const {test,expect}=require('@playwright/test');
async function start(page){
  // Functional tests must not depend on external font/tile server latency.
  await page.route('https://**/*',r=>r.abort());
  page.on('dialog',d=>d.accept());
  await page.addInitScript(()=>localStorage.setItem('sales_map_default_county_prompted','true'));
  await page.goto('/');
  await expect(page.locator('.client-card').first()).toBeVisible();
  await expect(page.locator('.leaflet-map-pane')).toHaveCSS('position','absolute');
  await expect(page.locator('.leaflet-control-zoom')).toBeVisible();
}
test('startup loads one dataset, mobile width and list remain usable',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:390,height:844});await start(page);
  expect(await page.evaluate(()=>Object.values(PARKS).filter(p=>p.clients).length)).toBe(1);
  expect((await page.locator('.sidebar').boundingBox()).width).toBeGreaterThan(380);
  await expect(page.locator('#collapsibleFilterSection')).toBeHidden();
  await page.locator('#btnViewList').click();
  const box=await page.locator('#clientList').boundingBox();expect(box.y).toBeLessThan(650);expect(box.height).toBeGreaterThan(80);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);
  await page.screenshot({path:'test-results/mobile.png'});
  expect(errors).toEqual([]);
});
test('custom client and all logs survive reload; unsafe text never becomes HTML',async({page})=>{
  await start(page);
  await page.locator('#btnAddClient').click();
  await page.locator('#addName').fill('<img src=x onerror="window.injected=true"> 測試客戶');
  await page.locator('#addRoad').fill('測試路');await page.locator('#addAddress').fill('測試地址');
  await page.locator('#formAddClient button[type=submit]').click();
  const id=await page.evaluate(()=>clients.find(c=>c.name.includes('測試客戶')).id);
  for(const summary of ['第一行\n第二行','<img src=x onerror="window.injected=true">']) {
    await page.evaluate(id=>openVisitLogModal(id),id);
    await page.locator('#logContact').fill('測試窗口');
    await page.locator('#logSummary').fill(summary);await page.locator('#formAddVisitLog button[type=submit]').click();
    await page.locator('#btnCloseVisitModal').click();
  }
  await page.reload();await expect(page.locator('.client-card').first()).toBeVisible();
  const saved=await page.evaluate(id=>clients.find(c=>c.id===id),id);
  expect(saved.visit_logs).toHaveLength(2);expect(saved.visit_logs[1].summary).toBe('第一行\n第二行');
  await page.evaluate(id=>openVisitLogModal(id),id);
  expect(await page.locator('#logHistoryList img').count()).toBe(0);
  expect(await page.evaluate(()=>window.injected)).toBeUndefined();
});
test('CSV cancel is inert, append and replacement survive reload, invalid input rejected',async({page})=>{
  await start(page);const before=await page.evaluate(()=>clients.length);
  const csv='公司名稱,所在路段,完整廠址,拜訪備忘與筆記\r\n匯入測試,測試路,測試址,"第一行\n第二行"';
  await page.locator('#fileInput').setInputFiles({name:'test.csv',mimeType:'text/csv',buffer:Buffer.from(csv)});
  await page.locator('#importCancel').click();expect(await page.evaluate(()=>clients.length)).toBe(before);
  await page.locator('#fileInput').setInputFiles({name:'test.csv',mimeType:'text/csv',buffer:Buffer.from(csv)});
  await page.locator('#importAppend').click();await page.reload();await expect(page.locator('.client-card').first()).toBeVisible();
  expect(await page.evaluate(()=>clients.find(c=>c.name==='匯入測試').notes)).toBe('第一行\n第二行');
  expect(await page.evaluate(()=>clients.find(c=>c.name==='匯入測試').lat)).toBeNull();
  await page.locator('#fileInput').setInputFiles({name:'test.csv',mimeType:'text/csv',buffer:Buffer.from(csv)});
  const download=page.waitForEvent('download');await page.locator('#importReplace').click();await download;
  await page.reload();await expect(page.locator('.client-card')).toHaveCount(1);
});
test('JSON backup round-trip restores custom clients, histories and settings',async({page})=>{
  await start(page);
  await page.evaluate(()=>{clients[0].visit_logs=[{id:'v_test',date:'2026-11-06',summary:'完整紀錄',contact:'測試',next_action:'再訪'}];clients.push(normalizeClient({id:99999999,name:'備份客戶'},currentPark,currentCounty));saveCurrentParkData();});
  const waiting=page.waitForEvent('download');await page.locator('#btnBackup').click();const download=await waiting;
  const buffer=require('fs').readFileSync(await download.path());
  await page.evaluate(()=>{localStorage.clear();localStorage.setItem('sales_map_default_county_prompted','true');});await page.reload();
  await expect(page.locator('.client-card').first()).toBeVisible();
  await page.locator('#fileInput').setInputFiles({name:'backup.json',mimeType:'application/json',buffer});
  const preRestore=page.waitForEvent('download');await page.locator('#importReplace').click();await preRestore;
  await page.reload();await expect(page.locator('.client-card').first()).toBeVisible();
  expect(await page.evaluate(()=>clients.some(c=>c.id===99999999))).toBe(true);
  expect(await page.evaluate(()=>clients[0].visit_logs[0].summary)).toBe('完整紀錄');
});
test('legacy storage migrates without discarding custom clients',async({page})=>{
  await page.addInitScript(()=>localStorage.setItem('sales_visit_clients_v744',JSON.stringify([{id:88888888,name:'舊版自建客戶',visit_logs:[{id:'v_old',summary:'歷史紀錄'}]}])));
  await start(page);
  expect(await page.evaluate(()=>clients.find(c=>c.id===88888888).visit_logs[0].summary)).toBe('歷史紀錄');
});
test('whole Taiwan overview renders bounded markers and latest navigation wins',async({page})=>{
  await start(page);
  await page.evaluate(()=>switchPark('all_taiwan'));
  expect(await page.evaluate(()=>clients.length)).toBe(13424);
  await page.evaluate(()=>updateMarkers(currentFiltered));
  expect(await page.evaluate(()=>Object.keys(markers).length)).toBeLessThan(1000);
  const storage=await page.evaluate(()=>{clients[0].status='已拜訪';return {saved:saveCurrentParkData(),length:localStorage.getItem(STORE_KEY).length};});
  expect(storage.saved).toBe(true);expect(storage.length).toBeLessThan(10000);
  await page.evaluate(()=>Promise.all([switchPark('guishan'),switchPark('zhongli')]));
  expect(await page.evaluate(()=>currentPark)).toBe('zhongli');
});
test('invalid CSV and malformed backups make no changes; quota failures preserve saved data',async({page})=>{
  await start(page);
  const snapshot=await page.evaluate(()=>localStorage.getItem(STORE_KEY));
  for(const [name,content] of [['bad.csv','公司名稱,緯度(Lat),經度(Lng)\n錯誤,999,121'],['bad.json','{"format":"sales-field-map","version":1,"parks":{"unknown":{"mode":"replace","clients":[]}},"settings":{}}']]) {
    await page.locator('#fileInput').setInputFiles({name,mimeType:'text/plain',buffer:Buffer.from(content)});
    await expect(page.locator('#modalImport')).toBeHidden();
    expect(await page.evaluate(()=>localStorage.getItem(STORE_KEY))).toBe(snapshot);
  }
  const result=await page.evaluate(()=>{
    const before=clients[0].status;const old=Storage.prototype.setItem;
    Storage.prototype.setItem=function(){throw new DOMException('Storage full','QuotaExceededError');};
    clients[0].status='已拜訪';const saved=saveCurrentParkData();Storage.prototype.setItem=old;
    return {saved,before,after:clients[0].status};
  });
  expect(result.saved).toBe(false);expect(result.after).toBe(result.before);
});
