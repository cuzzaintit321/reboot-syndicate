
(() => {
  const plans = [
    {
      name: "DIGITAL PRESENCE",
      price: "$299",
      summary: "Keep your business visible, updated, and professional.",
      included: [
        "Routine website content and maintenance updates",
        "Basic local SEO improvements",
        "Google Business Profile updates",
        "Monthly performance summary"
      ],
      ideal: "Small businesses that need a dependable online presence.",
      extras: "Website redesigns, additional pages, and advertising."
    },
    {
      name: "BUSINESS GROWTH",
      price: "$599",
      summary: "Build search visibility, engage customers, and track inquiries.",
      included: [
        "Everything in Digital Presence",
        "Scheduled social media content",
        "Expanded on-page and local SEO work",
        "Lead inquiry tracking",
        "Monthly marketing performance reporting"
      ],
      ideal: "Growing businesses ready for consistent marketing.",
      extras: "Paid ads, email campaigns, and reputation management."
    },
    {
      name: "GROWTH & AUTOMATION",
      price: "$999+",
      summary: "Connect marketing campaigns with smarter business systems.",
      included: [
        "Everything in Business Growth",
        "Lead capture and marketing automation",
        "Campaign coordination and optimization",
        "Conversion tracking and deeper reporting",
        "Ongoing workflow improvement"
      ],
      ideal: "Businesses looking to scale and automate repetitive work.",
      extras: "Custom integrations, advanced AI workflows, and ad spend."
    }
  ];

  const style = document.createElement("style");
  style.textContent = `
    .rs-clickable-plan { cursor:pointer; }
    .rs-clickable-plan:focus-visible {
      outline:3px solid #ff5c2a;outline-offset:4px;
    }
    .rs-clickable-plan:hover {
      border-color:#ff5c2a !important;
    }
    .rs-plan-overlay {
      position:fixed;inset:0;z-index:99999;
      background:rgba(0,0,0,.82);
      display:flex;align-items:center;justify-content:center;
      padding:20px;
    }
    .rs-plan-dialog {
      position:relative;width:min(760px,100%);
      max-height:90vh;overflow:auto;
      background:#151d20;color:#f4f1e8;
      border:1px solid #ff5c2a;
      padding:clamp(24px,4vw,45px);
      box-shadow:0 20px 80px #0009;
      font-family:'DM Sans',Arial,sans-serif;
    }
    .rs-plan-dialog h2 {
      font:900 clamp(36px,6vw,58px)/1 'Barlow Condensed',Impact,sans-serif;
      margin:15px 0;
    }
    .rs-plan-dialog h3 {
      color:#ff5c2a;font-size:13px;letter-spacing:.12em;
      margin:28px 0 12px;
    }
    .rs-plan-dialog p,.rs-plan-dialog li {
      line-height:1.7;color:#c8d0cc;
    }
    .rs-plan-dialog li {margin-bottom:8px;}
    .rs-plan-price {
      color:#ff5c2a;font-size:32px;font-weight:900;
    }
    .rs-plan-close {
      position:absolute;top:12px;right:15px;
      background:transparent;color:white;border:1px solid #ff5c2a;
      cursor:pointer;padding:8px 13px;font-size:20px;
    }
    .rs-plan-actions {
      display:flex;gap:12px;flex-wrap:wrap;margin-top:30px;
    }
    .rs-plan-actions a,.rs-plan-actions button {
      flex:1;min-width:180px;padding:17px 14px;
      text-align:center;text-decoration:none;
      font-weight:800;font-size:12px;cursor:pointer;
    }
    .rs-plan-quote {background:#ff5c2a;color:#101010;border:1px solid #ff5c2a;}
    .rs-plan-back {background:transparent;color:#ff5c2a;border:1px solid #ff5c2a;}
  `;
  document.head.appendChild(style);

  let previousFocus = null;

  function openPlan(plan) {
    previousFocus = document.activeElement;
    const overlay = document.createElement("div");
    overlay.className = "rs-plan-overlay";

    const dialog = document.createElement("section");
    dialog.className = "rs-plan-dialog";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", plan.name + " details");

    const close = document.createElement("button");
    close.className = "rs-plan-close";
    close.textContent = "×";
    close.setAttribute("aria-label", "Close details");
    dialog.appendChild(close);

    const heading = document.createElement("h2");
    heading.textContent = plan.name;
    dialog.appendChild(heading);

    const price = document.createElement("div");
    price.className = "rs-plan-price";
    price.textContent = plan.price + " / MONTH FROM";
    dialog.appendChild(price);

    const intro = document.createElement("p");
    intro.textContent = plan.summary;
    dialog.appendChild(intro);

    function section(title, items) {
      const h = document.createElement("h3");
      h.textContent = title;
      dialog.appendChild(h);
      if (Array.isArray(items)) {
        const ul = document.createElement("ul");
        items.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item;
          ul.appendChild(li);
        });
        dialog.appendChild(ul);
      } else {
        const p = document.createElement("p");
        p.textContent = items;
        dialog.appendChild(p);
      }
    }

    section("WHAT'S INCLUDED", plan.included);
    section("IDEAL FOR", plan.ideal);
    section("OPTIONAL ADD-ONS", plan.extras);

    const note = document.createElement("p");
    note.textContent =
      "Starting price only. Final scope, deliverables, setup fees, " +
      "advertising spend, and third-party costs are confirmed in a quote.";
    dialog.appendChild(note);

    const actions = document.createElement("div");
    actions.className = "rs-plan-actions";

    const quote = document.createElement("a");
    quote.className = "rs-plan-quote";
    quote.href = "/#consultation-form";
    quote.textContent = "REQUEST A CONSULTATION ↗";

    const back = document.createElement("button");
    back.className = "rs-plan-back";
    back.textContent = "BACK TO PLANS";

    actions.append(quote, back);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    function dismiss() {
      document.removeEventListener("keydown", onKey);
      overlay.remove();
      previousFocus?.focus?.();
    }

    function onKey(e) {
      if (e.key === "Escape") dismiss();
      if (e.key === "Tab") {
        const controls = [...dialog.querySelectorAll("button,a[href]")];
        const first = controls[0], last = controls[controls.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();first.focus();
        }
      }
    }

    close.onclick = dismiss;
    back.onclick = dismiss;
    quote.onclick = dismiss;
    overlay.addEventListener("click", e => {
      if (e.target === overlay) dismiss();
    });
    document.addEventListener("keydown", onKey);
    close.focus();
  }


  // Locate pricing cards by their actual content, not a guessed CSS class.
  const headings = [...document.querySelectorAll("h2,h3,h4,strong")];

  const cards = plans.map(plan => {
    const heading = headings.find(el =>
      el.textContent.trim().toUpperCase() === plan.name
    );

    if (!heading) return null;

    let node = heading.parentElement;

    while (node && node !== document.body) {
      const text = node.textContent.toUpperCase();
      const hasPrice = text.includes(plan.price);
      const hasButton = [...node.querySelectorAll("a,button")]
        .some(el => /DISCUSS THIS PLAN|VIEW DETAILS/i.test(el.textContent));

      if (hasPrice && hasButton) return node;

      node = node.parentElement;
    }

    return null;
  }).filter(Boolean);

  plans.forEach(plan => {
    const card = cards.find(el =>
      el.textContent.toUpperCase().includes(plan.name)
    );
    if (!card) {
      console.warn("Pricing card not found:", plan.name);
      return;
    }
    card.classList.add("rs-clickable-plan");
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", "View " + plan.name + " details");

    card.addEventListener("click", e => {
      if (e.target.closest("a,button")) return;
      openPlan(plan);
    });
    card.addEventListener("keydown", e => {
      if (e.target !== card) return;
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();openPlan(plan);
      }
    });

    const button = [...card.querySelectorAll("a,button")]
      .find(el => /DISCUSS THIS PLAN/i.test(el.textContent));

    if (button) {
      button.textContent = "VIEW DETAILS ↗";
      button.addEventListener("click", e => {
        e.preventDefault();
        e.stopPropagation();
        openPlan(plan);
      });
    }
  });
})();
