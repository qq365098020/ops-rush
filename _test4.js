const fs = require('fs');
const html = fs.readFileSync('/home/oiio/橙子的工作台/运营RUSH/index.html', 'utf8');
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// Replace `const app=new App()` with `return new App()` so we can catch the instance
const modifiedJs = js.replace('const app=new App()', 'var _app=new App(); if(typeof _appResult!=="undefined")_appResult=_app');

const mockDoc = { 
  getElementById: () => ({ classList: {add:()=>{},remove:()=>{}}, textContent: '', innerHTML: '', addEventListener: ()=>{}, style: {}, offsetHeight: 0 }),
  querySelector: () => ({ content: 'test' }),
  querySelectorAll: () => [],
  documentElement: { classList: {add:()=>{},remove:()=>{}} }
};
const mockLS = { getItem: () => null, setItem: () => {} };
const mockWin = { scrollY: 0, scrollTo: ()=>{}, location: {reload:()=>{}, hostname:'localhost'} };

try {
  let _appResult;
  new Function('document','localStorage','window','_appResult', modifiedJs)(mockDoc, mockLS, mockWin, _appResult);
  
  // Try to access via global
  const app = global._app || global.app;
  
  if (app) {
    console.log('App found, tasks:', app.tasks.length);
    
    // Test getTaskStatus
    let allOk = true;
    app.tasks.forEach(t => {
      try {
        const s = app.getTaskStatus(t);
        if (!s || !s.status) {
          console.log('BAD STATUS for', t.id, ':', JSON.stringify(s));
          allOk = false;
        }
      } catch(e) {
        console.log('getTaskStatus ERROR for', t.id, ':', e.message);
        allOk = false;
      }
    });
    if (allOk) console.log('All getTaskStatus OK');
    
    // Test openDetail
    app.tasks.forEach(t => {
      try {
        app.openDetail(t.id);
        console.log('openDetail(' + t.id + ') OK');
      } catch(e) {
        console.log('openDetail(' + t.id + ') ERROR:', e.message);
      }
    });
  } else {
    console.log('app not accessible');
  }
} catch(e) {
  console.log('ERROR:', e.message.substring(0, 200));
}
