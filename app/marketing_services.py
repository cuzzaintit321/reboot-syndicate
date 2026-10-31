from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')

# Detailed, individually scoped service information.
SERVICES = {
  "website-design": {
    "name": "Website Design & Development",
    "tag": "YOUR BUSINESS DESERVES A BETTER WEBSITE.",
    "lead": "A modern, mobile-friendly website should explain what you do, build trust, and make contacting you simple. We create clear, practical sites designed around your business and the people you want to reach.",
    "features": [
      [
        "Business websites",
        "Service pages, About pages, contact sections, testimonials supplied by you, and clear calls to action."
      ],
      [
        "Landing pages",
        "Focused pages for promotions, appointments, quote requests and advertising campaigns."
      ],
      [
        "Redesigns & responsiveness",
        "Improve outdated layouts, navigation, mobile readability, page structure and accessibility."
      ],
      [
        "Integrations & maintenance",
        "Contact forms, booking links, analytics, domain setup, hosting and ongoing updates as agreed."
      ]
    ],
    "deliverables": [
      "A page plan and design direction before build",
      "Responsive pages and working contact paths",
      "Basic launch checks for mobile, desktop, forms and key links",
      "An agreed handoff or ongoing maintenance plan"
    ],
    "bestFor": [
      "New businesses that need their first professional website",
      "Existing businesses with outdated, hard-to-use sites",
      "Campaigns needing focused landing pages"
    ],
    "faqs": [
      [
        "Can you work with my existing site?",
        "Often, yes. We review its platform and current setup before recommending a redesign, rebuild or smaller changes."
      ],
      [
        "Will hosting and ongoing updates be included?",
        "Hosting, maintenance and third-party services can be included in a scoped plan or quoted separately."
      ]
    ],
    "form": "Website Design"
  },
  "local-seo": {
    "name": "Search Engine Optimization",
    "tag": "GET FOUND WHEN CUSTOMERS SEARCH.",
    "lead": "SEO helps search engines understand your site and helps potential customers find relevant answers. We look at technical foundations, on-page content and local search opportunities, then prioritize realistic improvements.",
    "features": [
      [
        "SEO audits",
        "Review indexing, page titles, site structure, mobile experience, important redirects and basic performance."
      ],
      [
        "Keyword & competitor research",
        "Find relevant search topics and compare how competing sites present services."
      ],
      [
        "On-page improvements",
        "Improve headings, titles, page copy, internal links and metadata so pages are easier to understand."
      ],
      [
        "Local SEO support",
        "Align service areas, location information, relevant landing pages and business listings where appropriate."
      ]
    ],
    "deliverables": [
      "An initial findings list with priorities",
      "Agreed page-level changes and content recommendations",
      "Tracking/reporting setup where access allows",
      "A plain-language summary of completed work and next steps"
    ],
    "bestFor": [
      "Service companies relying on local discovery",
      "Websites with pages that are not attracting relevant search traffic",
      "Businesses launching new service pages"
    ],
    "faqs": [
      [
        "Can you guarantee first-page rankings?",
        "No. Search results depend on competition, search engines and many other factors. We focus on useful improvements and transparent reporting."
      ],
      [
        "How soon will SEO work show results?",
        "Timelines vary by site condition, competition and the changes made. We can set realistic review checkpoints without promising a particular outcome."
      ]
    ],
    "form": "Local SEO / Business Profile"
  },
  "google-business-profile": {
    "name": "Google Business Profile Management",
    "tag": "MAKE LOCAL DISCOVERY EASIER.",
    "lead": "An accurate, well-maintained business listing helps nearby customers understand your services, hours and contact options. We assist eligible businesses with the profile work that supports better local presentation.",
    "features": [
      [
        "Profile setup & cleanup",
        "Review eligibility, categories, service details, business descriptions and contact information."
      ],
      [
        "Photos & updates",
        "Organize appropriate business images, services and profile updates to keep information current."
      ],
      [
        "Local listing consistency",
        "Review key details across your website and relevant business directories."
      ],
      [
        "Review response support",
        "Help draft useful, professional replies to genuine customer feedback without fabricating reviews."
      ]
    ],
    "deliverables": [
      "A profile review and prioritized changes",
      "Agreed updates to listing details and imagery",
      "A simple maintenance checklist",
      "Summary of changes and items that require your approval"
    ],
    "bestFor": [
      "Local storefronts and service-area businesses",
      "Business owners with incomplete or outdated listing details",
      "Teams needing help maintaining business information"
    ],
    "faqs": [
      [
        "Do I keep ownership of my business listing?",
        "Yes. Your business should retain ownership and appropriate administrator access. We work through approved access."
      ],
      [
        "Can you get my business verified?",
        "We can guide the process for eligible businesses, but verification decisions are made by Google."
      ]
    ],
    "form": "Google Business Profile"
  },
  "social-media": {
    "name": "Social Media Management",
    "tag": "SHOW UP WITH PURPOSE.",
    "lead": "Consistent social content should look like your brand and speak to the customers you serve. We help with planning, visuals, captions and an agreed publishing rhythm rather than posting just to post.",
    "features": [
      [
        "Content calendars",
        "Plan topics, campaigns and a sensible posting schedule suited to your capacity."
      ],
      [
        "Visual posts & captions",
        "Produce branded graphics, creative concepts and copy for approved platforms."
      ],
      [
        "Page presentation",
        "Review profile bios, service links, branding and clear contact paths."
      ],
      [
        "Publishing & reporting",
        "Scheduling assistance and review of available audience and engagement data."
      ]
    ],
    "deliverables": [
      "A content direction and posting plan",
      "An agreed number of drafts or approved posts",
      "Brand-consistent visuals and captions",
      "Performance observations and next-step recommendations"
    ],
    "bestFor": [
      "Businesses with inconsistent posting",
      "Teams launching new products or services",
      "Local brands wanting a clearer visual identity online"
    ],
    "faqs": [
      [
        "Do you respond to messages and comments?",
        "Community management can be scoped separately with clear response and approval rules."
      ],
      [
        "Will you create videos and reels?",
        "Short-form video and editing can be scoped based on footage, requirements and available assets."
      ]
    ],
    "form": "Social Media Content"
  },
  "digital-advertising": {
    "name": "Paid Digital Advertising",
    "tag": "PUT YOUR BUDGET TO WORK.",
    "lead": "Paid campaigns need clear goals, appropriate audiences, landing pages and measurement. We help plan and manage Google Ads and Meta advertising within an agreed scope and approved budget.",
    "features": [
      [
        "Campaign strategy",
        "Define goals, audience, platform selection and relevant offers."
      ],
      [
        "Creative & landing pages",
        "Plan ad messages and suitable destinations that explain the offer and make next steps clear."
      ],
      [
        "Tracking setup",
        "Configure available conversion events, forms and reporting with proper access and consent."
      ],
      [
        "Optimization & reporting",
        "Review campaign data, test approved changes and explain what it means."
      ]
    ],
    "deliverables": [
      "Documented campaign objectives and setup",
      "Proposed creative and targeting for approval",
      "A reporting approach with key metrics",
      "Ongoing review and adjustment as contracted"
    ],
    "bestFor": [
      "Businesses testing lead-generation campaigns",
      "Brands promoting a specific product or service",
      "Owners wanting clearer insight into advertising spend"
    ],
    "faqs": [
      [
        "Is the advertising budget included?",
        "No. Advertising spend is paid separately from management fees unless a written agreement says otherwise."
      ],
      [
        "Can you guarantee leads or return on ad spend?",
        "No. Results depend on the offer, competition, budget and many other factors. We monitor and report outcomes."
      ]
    ],
    "form": "Digital Advertising"
  },
  "lead-automation": {
    "name": "AI & Marketing Automation",
    "tag": "MOVE LEADS FORWARD, NOT INTO A BLACK HOLE.",
    "lead": "When inquiries arrive through different channels, important follow-ups can be missed. We build practical workflows that help organize leads and guide the next step, with oversight where needed.",
    "features": [
      [
        "Lead capture",
        "Forms and intake steps that collect the information needed for a useful follow-up."
      ],
      [
        "CRM connections",
        "Connect lead records to supported customer-management tools where practical."
      ],
      [
        "Follow-up workflows",
        "Set up approved email notifications, reminders and scheduling handoffs."
      ],
      [
        "AI-assisted support",
        "Draft answers, classify inquiries or assist with chat workflows while keeping appropriate review controls."
      ]
    ],
    "deliverables": [
      "A simple process map and integration plan",
      "Configured workflows with test cases",
      "Basic failure handling and owner notifications",
      "A handoff guide for ongoing operation"
    ],
    "bestFor": [
      "Businesses missing inquiries or follow-ups",
      "Teams spending hours on repetitive admin",
      "Service providers scheduling consultations or appointments"
    ],
    "faqs": [
      [
        "Does automation mean every message is sent by AI?",
        "No. We can design approval steps and use automation only for clearly defined tasks."
      ],
      [
        "Can it connect to my existing software?",
        "We'll review the tools, available integrations and access limitations before committing to a build."
      ]
    ],
    "form": "Marketing Automation"
  },
  "branding-design": {
    "name": "Branding & Graphic Design",
    "tag": "LOOK LIKE A BRAND PEOPLE REMEMBER.",
    "lead": "A consistent visual identity makes your business easier to recognize. We help create or refine the design pieces that hold your website, marketing materials and social pages together.",
    "features": [
      [
        "Visual identity",
        "Logo direction, color palette, typography and overall brand treatment."
      ],
      [
        "Brand kits",
        "Simple usage guidance and reusable assets for consistent presentation."
      ],
      [
        "Marketing graphics",
        "Promotional graphics, social templates, banners and digital collateral."
      ],
      [
        "Print-ready concepts",
        "Business cards, flyers and selected branded materials within agreed specifications."
      ]
    ],
    "deliverables": [
      "A creative brief and visual direction",
      "Agreed concepts and revision rounds",
      "Approved final files in the agreed formats",
      "Basic usage guidance for brand consistency"
    ],
    "bestFor": [
      "New businesses creating an identity",
      "Brands that look inconsistent across channels",
      "Campaigns needing a unified visual style"
    ],
    "faqs": [
      [
        "How many logo revisions are included?",
        "Revision rounds and deliverables are defined in the project quote."
      ],
      [
        "Will I own my approved final assets?",
        "Usage and ownership terms are confirmed in writing, including any licensed third-party elements."
      ]
    ],
    "form": "Branding / Graphic Design"
  },
  "content-marketing": {
    "name": "Content Marketing & Copywriting",
    "tag": "SAY IT BETTER. MAKE IT USEFUL.",
    "lead": "Strong content helps customers understand what you offer and why it matters. We write and organize copy for websites, service pages, articles and campaigns with clarity and your voice in mind.",
    "features": [
      [
        "Website copy",
        "Headlines, About pages, service descriptions and customer-focused calls to action."
      ],
      [
        "Blog & article content",
        "Useful educational posts structured around real customer questions."
      ],
      [
        "Campaign messaging",
        "Email copy, captions and landing-page messages for specific offers."
      ],
      [
        "Editorial planning",
        "Topic ideas, content calendars and refresh recommendations."
      ]
    ],
    "deliverables": [
      "A short content brief and audience direction",
      "Drafts for the agreed pages or content pieces",
      "Defined editing/revision rounds",
      "Ready-to-publish approved copy"
    ],
    "bestFor": [
      "Businesses struggling to explain their services",
      "Websites with thin or outdated pages",
      "Brands planning a regular content program"
    ],
    "faqs": [
      [
        "Will you copy content from competitor websites?",
        "No. Research can inform positioning, but deliverables should be original and suitable for your business."
      ],
      [
        "Can content be optimized for SEO?",
        "Yes. We can combine clear writing with relevant topics and sensible on-page structure without keyword stuffing."
      ]
    ],
    "form": "Content Marketing / Copywriting"
  },
  "email-sms": {
    "name": "Email & SMS Marketing",
    "tag": "KEEP THE CONVERSATION GOING.",
    "lead": "Thoughtful customer communication can turn one inquiry into an ongoing relationship. We help build permission-based campaigns, useful follow-ups and clear subscriber journeys.",
    "features": [
      [
        "Newsletter campaigns",
        "Audience-focused updates, promotions and announcements."
      ],
      [
        "Customer journeys",
        "Welcome sequences, appointment reminders and follow-up workflows where appropriate."
      ],
      [
        "List organization",
        "Segments and sending workflows that fit your chosen platform."
      ],
      [
        "Consent & measurement",
        "Support for documented opt-ins, unsubscribe paths and relevant performance metrics."
      ]
    ],
    "deliverables": [
      "A campaign plan and message drafts",
      "Email layouts or SMS templates in the agreed tool",
      "Sending and opt-out checks before launch",
      "Campaign reporting and improvement ideas"
    ],
    "bestFor": [
      "Businesses with permission-based customer lists",
      "Service providers wanting consistent follow-up",
      "E-commerce brands announcing products or promotions"
    ],
    "faqs": [
      [
        "Can we message anyone whose number we have?",
        "No. We plan sending around applicable consent and opt-out requirements, and your business remains responsible for lawful outreach."
      ],
      [
        "Which email platform do you use?",
        "We can review your existing tools and propose a compatible setup before quoting."
      ]
    ],
    "form": "Email / SMS Marketing"
  },
  "reputation-management": {
    "name": "Reputation Management",
    "tag": "LET YOUR REAL CUSTOMER EXPERIENCE SPEAK.",
    "lead": "Your online reputation is shaped by customer experiences and how your business responds. We help organize ethical review requests, monitor feedback and communicate professionally.",
    "features": [
      [
        "Review request workflows",
        "Ask actual customers for honest feedback with appropriate timing and messaging."
      ],
      [
        "Monitoring",
        "Track review activity on agreed platforms when access is available."
      ],
      [
        "Response assistance",
        "Draft respectful responses to positive, critical and complicated feedback."
      ],
      [
        "Feedback insights",
        "Identify recurring service themes and opportunities to improve the customer experience."
      ]
    ],
    "deliverables": [
      "A review-request and response plan",
      "Templates for common response situations",
      "An agreed monitoring and reporting cadence",
      "Recommendations based on observed feedback"
    ],
    "bestFor": [
      "Local service businesses building customer trust",
      "Owners who struggle to keep up with reviews",
      "Businesses wanting a consistent response approach"
    ],
    "faqs": [
      [
        "Can you remove negative reviews?",
        "We can help identify reviews that may violate platform rules, but removals are decided by the platform."
      ],
      [
        "Do you provide paid or fake reviews?",
        "No. Review collection should be honest and comply with relevant platform policies."
      ]
    ],
    "form": "Reputation Management"
  },
  "ecommerce": {
    "name": "E-Commerce Solutions",
    "tag": "MAKE IT EASY TO SHOP.",
    "lead": "A good online storefront should make products easy to find, understand and purchase. We help plan and improve storefronts, catalogs and the practical integrations behind them.",
    "features": [
      [
        "Storefront setup",
        "Build or refine product collections, category pages and mobile shopping flows."
      ],
      [
        "Product presentation",
        "Support listings, product descriptions, images and navigation."
      ],
      [
        "Checkout integration",
        "Connect supported payment, shipping and tax-related tools within the platform's capabilities."
      ],
      [
        "Ongoing improvements",
        "Maintain approved updates and review available product and conversion data."
      ]
    ],
    "deliverables": [
      "A storefront structure and launch checklist",
      "An agreed set of configured pages/products",
      "Checkout and form testing within safe test modes",
      "A handoff or maintenance plan"
    ],
    "bestFor": [
      "Small brands launching online sales",
      "Existing shops with disorganized catalogs",
      "Businesses expanding beyond social-only storefronts"
    ],
    "faqs": [
      [
        "Can you move an existing store?",
        "Possibly. We first review the platform, product data and migration constraints."
      ],
      [
        "Are platform and payment fees included?",
        "Third-party fees and subscriptions are normally separate from the website project quote."
      ]
    ],
    "form": "E-commerce Store"
  },
  "analytics-conversion": {
    "name": "Analytics & Conversion Optimization",
    "tag": "UNDERSTAND THE NUMBERS. IMPROVE THE EXPERIENCE.",
    "lead": "Knowing what people do on your site makes it easier to prioritize changes. We set up practical analytics and examine where visitors engage, leave or contact your business.",
    "features": [
      [
        "Measurement planning",
        "Identify useful website actions such as form submissions, calls or booking clicks."
      ],
      [
        "Analytics setup",
        "Configure supported measurement and search reporting tools with appropriate consent handling."
      ],
      [
        "Dashboards & reports",
        "Present understandable activity and conversion indicators."
      ],
      [
        "Page improvements",
        "Review calls to action, mobile usability, navigation and landing-page messaging."
      ]
    ],
    "deliverables": [
      "A measurement map with agreed events",
      "Basic tracking checks and dashboard setup",
      "Reporting summary with limitations explained",
      "A prioritized set of improvement opportunities"
    ],
    "bestFor": [
      "Businesses unsure what their website contributes",
      "Campaigns needing conversion measurement",
      "Teams making decisions from scattered reports"
    ],
    "faqs": [
      [
        "Will you see every website visitor?",
        "No. Privacy settings, browser choices and consent can limit tracking, and reports may be incomplete."
      ],
      [
        "Can you promise a higher conversion rate?",
        "No. We can identify friction, propose changes and measure results when sufficient data exists."
      ]
    ],
    "form": "Analytics / Conversion Tracking"
  },
  "business-technology": {
    "name": "Business Technology Services",
    "tag": "SOLID SYSTEMS BEHIND EVERY GOOD BRAND.",
    "lead": "Business websites, email and marketing tools rely on domains, hosting and integrations working together. We help get the underlying technology configured and maintained.",
    "features": [
      [
        "Domains & DNS",
        "Domain setup, records, redirects and troubleshooting."
      ],
      [
        "Hosting & website care",
        "Hosting configuration, backups, updates and certificate management as scoped."
      ],
      [
        "Professional business email",
        "Mailbox setup, domain verification and basic delivery configuration."
      ],
      [
        "Software integrations",
        "Connect supported tools and simplify everyday operations where practical."
      ]
    ],
    "deliverables": [
      "An inventory of agreed technical changes",
      "Configurations and basic verification tests",
      "Access and ownership recommendations",
      "A maintenance or handoff checklist"
    ],
    "bestFor": [
      "New businesses setting up their online infrastructure",
      "Owners juggling several tools and subscriptions",
      "Websites with domain, email or hosting issues"
    ],
    "faqs": [
      [
        "Will I keep control of my domain?",
        "Yes. We recommend that domain and important service accounts remain owned by your business."
      ],
      [
        "Do you offer ongoing support?",
        "We can propose maintenance terms based on your systems and desired response scope."
      ]
    ],
    "form": "Business Technology / Hosting"
  },
  "it-support": {
    "name": "IT Support & Computer Repair",
    "tag": "WHEN THE TECH BREAKS, WE HELP.",
    "lead": "Reboot Syndicate began with practical technology support. We still offer local assistance with computers, connectivity and common business IT issues alongside our digital marketing services.",
    "features": [
      [
        "Computers & devices",
        "Desktop and laptop troubleshooting, setup and reasonable upgrade options."
      ],
      [
        "Wi-Fi & networking",
        "Router, wireless coverage and basic connectivity diagnostics."
      ],
      [
        "Backup planning",
        "Storage health checks, backup setup guidance and migration assessments."
      ],
      [
        "Small business IT",
        "Workstation setup and practical support for everyday office technology."
      ]
    ],
    "deliverables": [
      "A diagnosis or review of the reported issue",
      "An explanation of available options and estimated scope",
      "Approved repairs or configuration work",
      "Basic verification of the completed task"
    ],
    "bestFor": [
      "Titusville and nearby customers",
      "Small offices needing practical tech help",
      "People dealing with device or network problems"
    ],
    "faqs": [
      [
        "Do you provide on-site service?",
        "Availability and service location are confirmed after reviewing your request."
      ],
      [
        "Can you guarantee data recovery?",
        "No. Recovery may be impossible for damaged media; we'll explain feasibility and risks before proceeding."
      ]
    ],
    "form": "Small Business IT"
  }
}

# User-selected entry-level pricing. Displayed as estimates; individual scopes are quoted.
SERVICE_PRICING = {
    "website-design": {"starting": "$995", "unit": "/ project", "range": "$750–$1,500 / project"},
    "local-seo": {"starting": "$399", "unit": "/ mo", "range": "$300–$600 / mo"},
    "google-business-profile": {"starting": "$199", "unit": "/ setup", "range": "$150–$350 / setup"},
    "social-media": {"starting": "$399", "unit": "/ mo", "range": "$300–$700 / mo"},
    "digital-advertising": {"starting": "$399", "unit": "/ mo", "range": "$300–$650 / mo"},
    "lead-automation": {"starting": "$499", "unit": "/ setup", "range": "$400–$1,000 / setup"},
    "branding-design": {"starting": "$349", "unit": "/ project", "range": "$250–$700 / project"},
    "content-marketing": {"starting": "$125", "unit": "/ article", "range": "$80–$200 / article"},
    "email-sms": {"starting": "$249", "unit": "/ mo", "range": "$150–$400 / mo"},
    "reputation-management": {"starting": "$149", "unit": "/ mo", "range": "$100–$250 / mo"},
    "ecommerce": {"starting": "$1,499", "unit": "/ project", "range": "$1,200–$3,000 / project"},
    "analytics-conversion": {"starting": "$299", "unit": "/ setup", "range": "$200–$500 / setup"},
    "business-technology": {"starting": "$249", "unit": "/ setup", "range": "$150–$500 / setup"},
    "it-support": {"starting": "$95", "unit": "/ hr remote", "range": "$75–$150 / hr", "secondary": "$125 / hr onsite"},
}

@router.get('/marketing/{slug}')
def marketing_service(request: Request, slug: str):
    service = SERVICES.get(slug)
    if service is None:
        raise HTTPException(status_code=404, detail='Service not found')
    return templates.TemplateResponse(request, 'marketing_detail.html', {'service':service, 'slug':slug, 'pricing':SERVICE_PRICING[slug]})
