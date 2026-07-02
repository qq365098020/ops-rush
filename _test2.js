
const fs = require("fs");
const html = fs.readFileSync("/home/oiio/橙子的工作台/运营RUSH/index.html", "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const js = m[1];

// Mock minimal DOM
const doc = {
  getElementById: (id) => ({ classList: {add:()=>{},remove:()=>{}}, textContent: "", innerHTML: "", addEventListener: ()=>{}, style: {}, offsetHeight: 0 }),
  querySelector: () => ({ content: "test" }),
  querySelectorAll: () => []
};
const ls = { getItem: () => null, setItem: () => {} };
const win = { scrollY: 0, scrollTo: ()=>{} };

try {
  // Use Function constructor with mocks injected
  const fn = new Function("document", "localStorage", "window", js);
  fn(doc, ls, win);
  // Access app
  console.log("typeof app:", typeof app);
  console.log("Tasks:", app ? app.tasks.length : 0);
  console.log("openDetail exists:", typeof app.openDetail === "function");
  console.log("getTaskStatus exists:", typeof app.getTaskStatus === "function");
} catch(e) {
  console.log("ERROR:", e.message.substring(0,200));
}
