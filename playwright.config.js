const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
  testDir:'./tests', testMatch:'**/*.spec.js', timeout:30000, workers:1,
  use:{baseURL:'http://127.0.0.1:8769',headless:true,channel:process.platform==='win32'?'msedge':undefined},
  webServer:{command:'python -m http.server 8769 --bind 127.0.0.1',url:'http://127.0.0.1:8769',reuseExistingServer:false},
});
