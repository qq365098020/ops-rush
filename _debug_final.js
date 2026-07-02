const fs = require('fs');
let js = fs.readFileSync('/home/oiio/橙子的工作台/运营RUSH/index.html', 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
js = js.replace('const app=new App()', 'global.app=new App()');

// Inject console.log markers into openDetail
// After getTaskStatus:
js = js.replace(
  'const s=this.getTaskStatus(task);\n    let html=',
  'const s=this.getTaskStatus(task);console.log("M1:got status");\n    console.log("M2:building html");let html='
);

// After building, before set innerHTML
js = js.replace(
  "document.getElementById('detailContent').innerHTML=html;\n    document.getElementById('detailModal').classList.add('show');",
  "console.log('M3:setting html');document.getElementById('detailContent').innerHTML=html;console.log('M4:showing modal');document.getElementById('detailModal').classList.add('show');console.log('M5:done');"
);

const mockDoc = { 
  getElementById: () => ({ classList: {add:()=>{},remove:()=>{}}, textContent: '', innerHTML: '', addEventListener: ()=>{}, style: {}, offsetHeight: 0 }),
  querySelector: () => ({ content: 'test' }),
  querySelectorAll: () => [],
  documentElement: { classList: {add:()=>{},remove:()=>{}} }
};
const mockLS = { getItem: () => null, setItem: () => {} };
const mockWin = { scrollY: 0, scrollTo: ()=>{}, location: {reload:()=>{}, hostname:'localhost'} };

try {
  new Function('document','localStorage','window', js)(mockDoc, mockLS, mockWin);
  const app = global.app;
  console.log('--- Testing counterfeit_surrender ---');
  try { app.openDetail('counterfeit_surrender'); console.log('openDetail OK'); }
  catch(e) { console.log('ERROR at:', e.message); }
} catch(e) { console.log('FATAL:', e.message.substring(0,100)); }
