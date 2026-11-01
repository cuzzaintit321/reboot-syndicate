
(function () {
  'use strict';

  const PIXEL_ID = '1639724901213509';
  const KEY = 'rs_meta_consent';
  let initialized = false;

  function startPixel() {
    if (initialized) return;
    initialized = true;

    !function(f,b,e,v,n,t,s) {
      if(f.fbq)return;
      n=f.fbq=function(){
        n.callMethod ?
        n.callMethod.apply(n,arguments) :
        n.queue.push(arguments)
      };
      if(!f._fbq)f._fbq=n;
      n.push=n;
      n.loaded=!0;
      n.version='2.0';
      n.queue=[];
      t=b.createElement(e);
      t.async=!0;
      t.src=v;
      s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s);
    }(window,document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');

    fbq('init', PIXEL_ID);
    fbq('track', 'PageView');
  }

  function consentBanner() {
    if (localStorage.getItem(KEY)) return;

    const banner = document.createElement('div');
    banner.id = 'rs-cookie-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie preferences');

    banner.style.cssText = `
      position:fixed;bottom:20px;left:20px;right:20px;
      z-index:99999;max-width:600px;margin:auto;
      padding:20px;background:#17191d;color:white;
      border:1px solid #ff5c2a;border-radius:12px;
      box-shadow:0 10px 40px #0008;
      font:14px/1.5 Arial,sans-serif;
    `;

    banner.innerHTML = `
      <strong style="font-size:17px">YOUR PRIVACY MATTERS</strong>
      <p>We use optional Meta tracking to understand website
      visits and measure advertising performance. You can
      accept or reject this tracking.</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <button type="button" id="rs-accept">ACCEPT</button>
        <button type="button" id="rs-reject">REJECT</button>
      </div>
    `;

    document.body.appendChild(banner);

    for (const id of ['rs-accept', 'rs-reject']) {
      const button = document.getElementById(id);
      button.style.cssText = `
        background:${id === 'rs-accept' ? '#ff5c2a' : '#34373b'};
        color:white;border:0;border-radius:6px;
        padding:10px 20px;cursor:pointer;font-weight:bold;
      `;
    }

    document.getElementById('rs-accept').onclick = () => {
      localStorage.setItem(KEY, 'accepted');
      banner.remove();
      startPixel();
    };

    document.getElementById('rs-reject').onclick = () => {
      localStorage.setItem(KEY, 'rejected');
      banner.remove();
    };
  }

  function initialize() {
    if (localStorage.getItem(KEY) === 'accepted') {
      startPixel();
    } else {
      consentBanner();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
