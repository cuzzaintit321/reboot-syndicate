
(() => {
  if (document.querySelector(".rs-social-links")) return;

  const style = document.createElement("style");
  style.textContent = `
    .rs-social-links {
      display:flex;
      align-items:center;
      gap:14px;
      flex-wrap:wrap;
    }
    .rs-social-links a {
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:36px;
      height:36px;
      color:#f4f1e8;
      border:1px solid #465154;
      transition:color .2s,border-color .2s,background .2s;
    }
    .rs-social-links a:hover,
    .rs-social-links a:focus-visible {
      color:#ff5c2a;
      border-color:#ff5c2a;
      background:#ff5c2a12;
    }
    .rs-social-links svg {
      width:19px;
      height:19px;
      fill:none;
      stroke:currentColor;
      stroke-width:2;
      stroke-linecap:round;
      stroke-linejoin:round;
    }
    .rs-social-links .rs-facebook {
      font:bold 23px Arial,sans-serif;
      line-height:1;
    }
    .site-header .rs-social-links {
      margin-left:10px;
    }
    footer .rs-social-links {
      justify-self:start;
    }
    @media(max-width:900px) {
      .site-header .rs-social-links {
        margin-left:0;
      }
    }
  `;
  document.head.appendChild(style);

  const facebook = "https://www.facebook.com/RebootSyndicate";
  const instagram = "https://www.instagram.com/rebootsyndicate321/";

  function createLinks() {
    const wrap = document.createElement("div");
    wrap.className = "rs-social-links";

    const fb = document.createElement("a");
    fb.href = facebook;
    fb.target = "_blank";
    fb.rel = "noopener noreferrer";
    fb.setAttribute("aria-label", "Reboot Syndicate on Facebook");
    fb.title = "Facebook";
    fb.innerHTML = '<span class="rs-facebook" aria-hidden="true">f</span>';

    const ig = document.createElement("a");
    ig.href = instagram;
    ig.target = "_blank";
    ig.rel = "noopener noreferrer";
    ig.setAttribute("aria-label", "Reboot Syndicate on Instagram");
    ig.title = "Instagram";
    ig.innerHTML = `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="2" y="2" width="20" height="20" rx="5"/>
        <circle cx="12" cy="12" r="4"/>
        <circle cx="18" cy="6" r="1" fill="currentColor" stroke="none"/>
      </svg>`;

    wrap.append(fb, ig);
    return wrap;
  }

  const header = document.querySelector(".site-header");
  const footer = document.querySelector("footer");

  if (header) header.appendChild(createLinks());
  if (footer) footer.appendChild(createLinks());
})();
