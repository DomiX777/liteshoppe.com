const { chromium } = require('playwright');
// usage: node render2.js URL OUTDIR FPS DURATION [times,comma] [workers]
(async()=>{const [url,out,fps,dur,times,wk]=process.argv.slice(2);
const list = times && times!=='-' ? times.split(',').map(Number) : Array.from({length:Math.round(dur*fps)},(_,i)=>i/fps);
const N=Math.min(parseInt(wk||'4'),list.length);const b=await chromium.launch();
await Promise.all(Array.from({length:N},async(_,w)=>{
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto(url,{waitUntil:'networkidle'});
  await p.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});
  for(let i=w;i<list.length;i+=N){
    await p.evaluate(t=>window.seek(t),list[i]);
    await p.screenshot({path:`${out}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});
  }
}));
console.log('frames',list.length);await b.close();})();
