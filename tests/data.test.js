const {test}=require('node:test');
const assert=require('node:assert/strict');
const d=require('../data-tools');
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
