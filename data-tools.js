/* Shared, dependency-free data validation. Also exercised by Node regression tests. */
(function (root) {
  const fields = ['name', 'road', 'address', 'industry', 'contact', 'phone', 'notes'];
  const text = value => String(value ?? '');
  function escapeHtml(value) {
    return text(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function validCoordinates(c) {
    return Number.isFinite(c.lat) && Number.isFinite(c.lng) && Math.abs(c.lat) <= 90 && Math.abs(c.lng) <= 180;
  }
  function normalizeClient(c, pid, county) {
    if (!c || !Number.isSafeInteger(c.id) || c.id < 1 || !text(c.name).trim()) throw Error('客戶編號或公司名稱不正確');
    const out = {id:c.id, park_id:pid, county_id:county};
    for (const key of fields) out[key] = text(c[key]);
    out.status = ['尚未拜訪','待拜訪','洽談中','已拜訪'].includes(c.status) ? c.status : '尚未拜訪';
    out.is_listed = c.is_listed === '是' ? '是' : '否';
    out.lat = validCoordinates(c) ? c.lat : null;
    out.lng = validCoordinates(c) ? c.lng : null;
    if (c.visit_logs !== undefined && !Array.isArray(c.visit_logs)) throw Error('拜訪紀錄格式不正確');
    out.visit_logs = (c.visit_logs || []).map((log, i) => {
      if (!log || typeof log !== 'object') throw Error('拜訪紀錄格式不正確');
      const result = {id:/^[\w-]+$/.test(text(log.id)) ? text(log.id) : `v_${c.id}_${i}`};
      for (const key of ['date','contact','outcome','next_action','summary']) result[key] = text(log[key]);
      result.created_at = Number.isFinite(log.created_at) ? log.created_at : 0;
      return result;
    });
    return out;
  }
  function mergeClients(base, saved, pid, county) {
    const result = new Map(base.map(c => [c.id, normalizeClient(c, pid, county)]));
    for (const raw of saved) {
      const c = normalizeClient(raw, pid, county);
      const original = result.get(c.id);
      // Official attributes may change; local progress and newly-created clients survive.
      result.set(c.id, original ? {...original, status:c.status, notes:c.notes, visit_logs:c.visit_logs} : c);
    }
    return [...result.values()];
  }
  function parseCSV(input) {
    const rows = []; let row = [], value = '', quoted = false, closed = false;
    const source = input.replace(/^\uFEFF/, '');
    for (let i=0; i<source.length; i++) {
      const c=source[i];
      if (quoted) {
        if (c === '"' && source[i+1] === '"') {value+='"'; i++;}
        else if (c === '"') {quoted=false; closed=true;}
        else value+=c;
      } else if (c === '"' && !value && !closed) quoted=true;
      else if (c === ',') {row.push(value); value=''; closed=false;}
      else if (c === '\n' || c === '\r') {
        if (c === '\r' && source[i+1] === '\n') i++;
        row.push(value); if(row.some(v=>v.trim())) rows.push(row); row=[]; value=''; closed=false;
      } else {
        if (closed && c.trim()) throw Error('CSV 引號後有不合法字元');
        value+=c;
      }
    }
    if (quoted) throw Error('CSV 引號未關閉');
    row.push(value); if(row.some(v=>v.trim())) rows.push(row);
    return rows;
  }
  function csvCell(value) {
    let s=text(value);
    if (/^[\s]*[=+@-]/.test(s) || /^[\t\r\n]/.test(s)) s="'"+s;
    return '"'+s.replace(/"/g,'""')+'"';
  }
  const api={escapeHtml,validCoordinates,normalizeClient,mergeClients,parseCSV,csvCell};
  if(typeof module!=='undefined') module.exports=api;
  else root.SalesData=api;
})(globalThis);
