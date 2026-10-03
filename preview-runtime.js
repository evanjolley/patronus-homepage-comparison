(() => {
  let swiper;
  const root = document.querySelector('.swiper.is-wow_new');
  function init() {
    if (!root || swiper || typeof Swiper !== 'function') return;
    swiper = new Swiper(root, {
      slidesPerView:'auto', spaceBetween:8, loop:true,
      autoplay:{delay:3000,disableOnInteraction:false},
      mousewheel:{forceToAxis:true,sensitivity:1,releaseOnEdges:true},
      breakpoints:{320:{spaceBetween:0},992:{spaceBetween:8}}
    });
    root.querySelectorAll('.wow_research-slide_component').forEach(card => {
      card.tabIndex=0;
      const details=card.querySelector('.wow_research-list_wrapper');
      const update=()=>{
        const open=card.matches(':hover') || card.contains(document.activeElement);
        if(innerWidth>=992)details.style.height=open?details.scrollHeight+'px':'0px';
        if(open)swiper.autoplay.stop();else swiper.autoplay.start();
      };
      card.addEventListener('mouseenter',update);card.addEventListener('mouseleave',update);
      card.addEventListener('focusin',update);card.addEventListener('focusout',()=>requestAnimationFrame(update));
    });
  }
  new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting))init()},{threshold:.05}).observe(root);
  window.addEventListener('message',e=>{
    if(e.source!==parent || e.origin!==location.origin)return;
    if(e.data?.type==='compare-active'){
      if(e.data.active){swiper?.update();swiper?.autoplay.start();window.ScrollTrigger?.refresh();}
      else swiper?.autoplay.stop();
    }
  });
  // The preview preserves form appearance without sending subscriptions.
  document.querySelectorAll('form').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();e.stopImmediatePropagation();},true));
  window.addEventListener('load',()=>{window.ScrollTrigger?.refresh();parent.postMessage({type:'compare-ready'},location.origin);});
})();
