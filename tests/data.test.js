const {test}=require('node:test');
const assert=require('node:assert/strict');
const d=require('../data-tools');
test('vendored Leaflet bytes match published subresource integrity hashes',()=>{
  const fs=require('fs'),crypto=require('crypto');
  for(const [file,hash] of [['leaflet.css','p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY='],['leaflet.js','20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=']]) {
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync('vendor/leaflet/'+file)).digest('base64'),hash);
  }
});
test('quoted multiline CSV preserves quotes, commas, BOM and CRLF',()=>{
  assert.deepEqual(d.parseCSV('\ufeffname,notes\r\n"客戶","第一行\r\n第二行,""好"""\r\n'),[['name','notes'],['客戶','第一行\r\n第二行,"好"']]);
  assert.throws(()=>d.parseCSV('name,notes\na,"broken'));
});
test('CSV escaping blocks spreadsheet formulas and escapes quotes',()=>{
  for(const value of ['=1+1',' +1','-1','@SUM(A1)','\ttext'])assert.ok(d.csvCell(value).startsWith('"\''));
  assert.equal(d.csvCell('a"b'),'"a""b"');
});
test('official update preserves progress and custom clients',()=>{
  const result=d.mergeClients([{id:1,name:'新名稱'}],[{id:1,name:'舊名稱',status:'已拜訪',notes:'筆記',visit_logs:[{id:'v_1',summary:'紀錄'}]},{id:2,name:'自建客戶'}],'park','county');
  assert.equal(result.length,2);assert.equal(result[0].name,'新名稱');assert.equal(result[0].status,'已拜訪');assert.equal(result[0].visit_logs[0].summary,'紀錄');
});
test('missing coordinates stay unlocated, invalid IDs rejected and text escaped',()=>{
  assert.equal(d.normalizeClient({id:1,name:'測試'},'p','c').lat,null);
  assert.equal(d.validCoordinates({lat:95,lng:121}),false);
  assert.equal(d.validCoordinates({lat:null,lng:null}),false);
  assert.throws(()=>d.normalizeClient({id:'1);alert(1)',name:'bad'},'p','c'));
  assert.equal(d.escapeHtml('<img onerror="x">'),'&lt;img onerror=&quot;x&quot;&gt;');
});
test('search normalization unifies Taiwan variants, fullwidth text and phone digits',()=>{
  assert.equal(d.normalizeSearchText('臺灣（臺中）ＡＢＣ-123'),'台灣 台中 abc 123');
  assert.equal(d.compactPhoneDigits('03-452-8899#12'),'03452889912');
  const haystack=d.buildClientSearchHaystack({
    name:'臺灣精密股份有限公司',
    phone:'03-452-8899',
    visit_logs:[{contact:'林經理',summary:'預計下週報價 RICOH IM C3010'}]
  }, '桃園市 中壢產業園區');
  assert.ok(haystack.includes('台灣精密'));
  assert.ok(haystack.includes('034528899'));
  assert.ok(haystack.includes('林經理'));
  assert.ok(haystack.includes('imc3010') || haystack.includes('im c3010'));
});

