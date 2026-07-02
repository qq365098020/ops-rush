const fs = require('fs');
const html = fs.readFileSync('/home/oiio/橙子的工作台/运营RUSH/index.html', 'utf8');
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// Minimal DOM mock
global.document = { 
  getElementById: () => ({ classList: {add:()=>{},remove:()=>{}}, textContent: '', innerHTML: '', addEventListener: ()=>{}, style: {}, offsetHeight: 0 }),
  querySelector: () => ({ content: 'test' }),
  querySelectorAll: () => [],
  documentElement: { classList: {add:()=>{},remove:()=>{}} }
};
global.localStorage = { getItem: () => null, setItem: () => {} };
global.window = { scrollY: 0, scrollTo: ()=>{}, location: {reload:()=>{}, hostname:'localhost'} };
global.setInterval = () => 1;
global.setTimeout = () => 1;
global.clearTimeout = () => {};
global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
global.requestAnimationFrame = () => 1;
global.XMLHttpRequest = function() { this.open = ()=>{}, this.send = ()=>{} };
global.URL = { createObjectURL: ()=>'', revokeObjectURL: ()=>{} };
global.Blob = function(){};
global.navigator = {};
global.location = { reload: () => {}, hostname: 'localhost' };

try {
  new Function('document','localStorage','window','fetch','requestAnimationFrame','XMLHttpRequest','URL','Blob','navigator','location',js)
    (document, localStorage, window, fetch, requestAnimationFrame, XMLHttpRequest, URL, Blob, navigator, location);
  
  console.log('App created successfully');
  console.log('Tasks:', app.tasks.length);
  
  // Test getTaskStatus for every task
  let allOk = true;
  app.tasks.forEach(t => {
    try {
      const s = app.getTaskStatus(t);
      if (!s || !s.status) {
        console.log('  BAD STATUS for', t.id, ':', JSON.stringify(s));
        allOk = false;
      }
    } catch(e) {
      console.log('  ERROR for', t.id, ':', e.message);
      allOk = false;
    }
  });
  
  if (allOk) console.log('All getTaskStatus calls succeeded');
  
  // Test openDetail for each task
  app.tasks.forEach(t => {
    try {
      app.openDetail(t.id);
      console.log('  openDetail(' + t.id + ') OK');
    } catch(e) {
      console.log('  openDetail(' + t.id + ') ERROR:', e.message);
    }
  });
  
} catch(e) {
  console.log('INIT FAILED:', e.message);
  process.exit(1);
}
