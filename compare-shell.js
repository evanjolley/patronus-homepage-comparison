// Original/Revised comparison shell. Each route's index.html sets window.COMPARE = {order: [...section keys in page order]}.
const frames={original:document.getElementById('original'),revised:document.getElementById('revised')};
const config=window.COMPARE;
let active='revised';
const sectionControl=document.getElementById('section');
function landmarks(frame){return [...frame.contentDocument.querySelectorAll('[data-compare-section]')];}
// Products: the numbered sections share one pinned, scroll-scrubbed block on desktop and stack on mobile.
function stepsTrigger(frame){
 // Only the desktop layout scrubs; on mobile the pinned grid is hidden and the sections stack.
 const ST=frame.contentWindow.ScrollTrigger,grid=frame.contentDocument.querySelector('.product_steps-grid');
 if(!ST||!grid||frame.contentWindow.getComputedStyle(grid).display==='none')return null;
 return ST.getAll().find(t=>t.pin&&t.trigger&&t.trigger.classList.contains('product_steps-component'));
}
function stepThresholds(st){
 // Progress at which sections 02 and 03 take over: the moments the previous text fades out.
 const tl=st.animation,total=tl.duration();
 return tl.getChildren().filter(t=>t.vars.opacity===0).map(t=>(t.startTime()+t.duration())/total).sort((a,b)=>a-b);
}
function stepSettled(st,n){
 // Progress at which section n's text has finished sliding into place.
 const tl=st.animation,tween=tl.getChildren().find(t=>t.vars.y!==undefined&&t.targets()[0].id==='text_'+n);
 return tween?(tween.startTime()+tween.duration())/tl.duration():0;
}
function stepKey(frame){
 const st=stepsTrigger(frame);
 if(st){const p=st.progress,[t2,t3]=stepThresholds(st);return 'step-'+(p>=t3?3:p>=t2?2:1);}
 let n=1;[1,2,3].forEach(i=>{const el=frame.contentDocument.getElementById('mobile-number_'+i);if(el&&el.getBoundingClientRect().top<=120)n=i;});
 return 'step-'+n;
}
function alignStep(frame,n,inset){
 const win=frame.contentWindow,st=stepsTrigger(frame);
 if(st){win.scrollTo({top:Math.ceil(st.start+(n>1?stepSettled(st,n):0)*(st.end-st.start)),behavior:'instant'});return;}
 const el=frame.contentDocument.getElementById('mobile-number_'+n);
 if(el)win.scrollTo({top:Math.max(0,el.getBoundingClientRect().top+win.scrollY-inset),behavior:'instant'});
}
function position(frame){
 const y=frame.contentWindow.scrollY;
 const items=landmarks(frame);
 let index=0;
 for(let i=0;i<items.length;i++)if(items[i].getBoundingClientRect().top<=120)index=i;
 const node=items[index];if(!node)return {key:'hero',fraction:0};
 const start=node.getBoundingClientRect().top+y;
 const end=items[index+1]?items[index+1].getBoundingClientRect().top+y:frame.contentDocument.documentElement.scrollHeight;
 return {key:node.dataset.compareSection,fraction:(y-start)/Math.max(end-start,1)};
}
function align(frame,pos){
 const items=landmarks(frame);let i=items.findIndex(n=>n.dataset.compareSection===pos.key);
 if(i<0){
  // Section absent from this version: continue at the next section that both share.
  const keys=config.order.slice(config.order.indexOf(pos.key)+1);
  for(const k of keys){i=items.findIndex(n=>n.dataset.compareSection===k);if(i>=0)break;}
  pos={fraction:0};
 }
 const node=items[i];if(!node)return;
 const win=frame.contentWindow,start=node.getBoundingClientRect().top+win.scrollY;
 const end=items[i+1]?items[i+1].getBoundingClientRect().top+win.scrollY:frame.contentDocument.documentElement.scrollHeight;
 win.scrollTo({top:Math.max(0,start+pos.fraction*(end-start)-(pos.inset||0)),behavior:'instant'});
}
function show(version){
 active=version;
 try{sessionStorage.setItem('compare-version',version);}catch(e){}
 Object.entries(frames).forEach(([name,frame])=>{
  const on=name===active;frame.classList.toggle('hidden',!on);frame.setAttribute('aria-hidden',String(!on));frame.tabIndex=on?0:-1;
  if(frame.contentDocument&&frame.contentDocument.readyState!=='loading')frame.contentWindow.postMessage({type:'compare-active',active:on},location.origin);
 });
 document.querySelectorAll('[data-version]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.version===active)));
}
function choose(version){
 if(version===active)return;
 const pos=position(frames[active]);
 show(version);
 align(frames[active],pos);
}
document.querySelectorAll('[data-version]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.version)));
sectionControl.addEventListener('change',()=>{
 const key=sectionControl.value,inset=key==='hero'?0:(active==='original'?150:110);
 if(key.startsWith('step-'))alignStep(frames[active],Number(key.slice(5)),inset);
 else align(frames[active],{key,fraction:0,inset});
});
// The selected version carries over between pages of the comparison site.
try{if(sessionStorage.getItem('compare-version')==='original')show('original');}catch(e){}
Object.entries(frames).forEach(([name,frame])=>frame.addEventListener('load',()=>{
 frame.contentWindow.postMessage({type:'compare-active',active:name===active},location.origin);
 let pending=false;
 frame.contentWindow.addEventListener('scroll',()=>{
  if(name!==active||pending)return;pending=true;
  requestAnimationFrame(()=>{
   let key=position(frame).key;
   if(key==='steps')key=stepKey(frame);
   if([...sectionControl.options].some(o=>o.value===key))sectionControl.value=key;
   pending=false;
  });
 },{passive:true});
}));
