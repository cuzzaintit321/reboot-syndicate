from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from app.marketing_services import SERVICES
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
BASE = "https://rebootsyndicate.com"
INDUSTRIES = {'contractors': {'name': 'Construction & Contractors',
                 'title': 'Website Design & Marketing for Contractors',
                 'headline': 'Turn project photos into qualified estimate requests.',
                 'audience': 'General contractors, carpenters, remodelers and concrete companies',
                 'challenge': 'Homeowners compare workmanship, scope and reliability before requesting an '
                              'estimate. Show what you build, where you work and how your quoting process '
                              'works.',
                 'examples': 'A bathroom remodel gallery with project scope and an estimate form; a concrete '
                             'patio campaign with a dedicated landing page; follow-up reminders for open '
                             'estimates.',
                 'services': ['website-design',
                              'local-seo',
                              'digital-advertising',
                              'lead-automation',
                              'reputation-management'],
                 'question': 'Can you build a project portfolio?',
                 'answer': 'Yes. We can organize approved photos by project type and add useful descriptions '
                           'without inventing project results.',
                 'description': 'Website Design & Marketing for Contractors. Reboot Syndicate helps general '
                                'contractors, carpenters, remodelers and concrete companies in Brevard '
                                'County and remotely.'},
 'restaurants': {'name': 'Restaurants & Food Trucks',
                 'title': 'Digital Marketing for Restaurants & Food Trucks',
                 'headline': 'Make the next meal an easy decision.',
                 'audience': 'Independent restaurants, cafés, bakeries and mobile food vendors',
                 'challenge': 'Customers need current menus, hours, locations and ordering options. Food '
                              'trucks also need a reliable way to announce changing stops.',
                 'examples': 'A mobile menu with ordering links; a weekly food truck schedule; a catering '
                             'inquiry page with group size and date fields.',
                 'services': ['website-design',
                              'google-business-profile',
                              'social-media',
                              'digital-advertising',
                              'email-sms'],
                 'question': 'Can you keep our existing ordering system?',
                 'answer': 'Yes, where supported. We can link to or integrate your existing ordering '
                           'platform rather than requiring a replacement.',
                 'description': 'Digital Marketing for Restaurants & Food Trucks. Reboot Syndicate helps '
                                'independent restaurants, cafés, bakeries and mobile food vendors in Brevard '
                                'County and remotely.'},
 'landscaping': {'name': 'Landscaping & Tree Services',
                 'title': 'SEO & Marketing for Landscaping Companies',
                 'headline': 'Put your outdoor work in front of the right property owners.',
                 'audience': 'Landscapers, tree care companies, irrigation specialists and lawn services',
                 'challenge': 'Customers often need to distinguish recurring maintenance from one-time '
                              'projects. Separate these offerings and explain service areas, scheduling and '
                              'quote requirements.',
                 'examples': 'A seasonal irrigation inspection campaign; tree care service pages; a '
                             'landscape project gallery with maintenance inquiry options.',
                 'services': ['local-seo',
                              'website-design',
                              'google-business-profile',
                              'reputation-management',
                              'digital-advertising'],
                 'question': 'Can you promote recurring maintenance plans?',
                 'answer': 'Yes. We can create clear plan pages and campaigns, with pricing and terms '
                           'approved by your business.',
                 'description': 'SEO & Marketing for Landscaping Companies. Reboot Syndicate helps '
                                'landscapers, tree care companies, irrigation specialists and lawn services '
                                'in Brevard County and remotely.'},
 'automotive': {'name': 'Automotive & Detailing',
                'title': 'Digital Marketing for Auto Repair & Detailing',
                'headline': 'Help drivers find the right service when they need it.',
                'audience': 'Auto repair shops, mobile mechanics, detailers and specialty automotive '
                            'businesses',
                'challenge': 'Drivers want clear service descriptions, convenient scheduling and confidence '
                             'in who will handle their vehicle. Mobile operators also need clear service '
                             'boundaries.',
                'examples': 'Separate brake repair and detailing pages; a mobile mechanic appointment form; '
                            'a detailing portfolio organized by package.',
                'services': ['local-seo',
                             'website-design',
                             'google-business-profile',
                             'reputation-management',
                             'lead-automation'],
                'question': 'Can we keep our appointment software?',
                'answer': 'We can review your existing booking tool and connect supported links or '
                          'integrations.',
                'description': 'Digital Marketing for Auto Repair & Detailing. Reboot Syndicate helps auto '
                               'repair shops, mobile mechanics, detailers and specialty automotive '
                               'businesses in Brevard County and remotely.'},
 'beauty': {'name': 'Beauty & Personal Care',
            'title': 'Website Design & Marketing for Salons',
            'headline': 'Showcase your specialty and make appointments easier.',
            'audience': 'Hair stylists, salons, barbers, nail studios and beauty professionals',
            'challenge': 'Clients often choose based on portfolios, specialties and availability. Make it '
                         'easy to understand services, prepare for an appointment and find booking details.',
            'examples': 'A vivid hair color portfolio; a bridal styling inquiry page; permission-based '
                        'appointment reminders and rebooking campaigns.',
            'services': ['website-design', 'social-media', 'local-seo', 'email-sms', 'branding-design'],
            'question': 'Do I need to replace my booking platform?',
            'answer': 'No. We can build around an existing supported booking platform and improve the path '
                      'from discovery to booking.',
            'description': 'Website Design & Marketing for Salons. Reboot Syndicate helps hair stylists, '
                           'salons, barbers, nail studios and beauty professionals in Brevard County and '
                           'remotely.'},
 'real-estate': {'name': 'Real Estate & Property Management',
                 'title': 'Digital Marketing for Real Estate & Property Managers',
                 'headline': 'Turn property information into useful inquiries.',
                 'audience': 'Real estate professionals, commercial brokers and property managers',
                 'challenge': 'Prospects need clear property details, availability and contact paths. Owners '
                              'and tenants may require different information, so separate their journeys.',
                 'examples': 'A commercial leasing inquiry page; property management service pages for '
                             'owners; an approved listing showcase with inquiry tracking.',
                 'services': ['website-design',
                              'local-seo',
                              'content-marketing',
                              'lead-automation',
                              'analytics-conversion'],
                 'question': 'Can you work with existing listing systems?',
                 'answer': 'We review available integrations and permissions before proposing a solution. '
                           'Housing advertising must follow applicable rules and platform restrictions.',
                 'description': 'Digital Marketing for Real Estate & Property Managers. Reboot Syndicate '
                                'helps real estate professionals, commercial brokers and property managers '
                                'in Brevard County and remotely.'},
 'home-services': {'name': 'Home Services',
                   'title': 'Local SEO & Marketing for Home Service Businesses',
                   'headline': 'Be easier to find when customers need help.',
                   'audience': 'HVAC, plumbing, electrical, pressure washing, cleaning and junk removal '
                               'companies',
                   'challenge': 'Urgent repair searches differ from planned maintenance. Clear service '
                                'pages, click-to-call links and quote forms help customers choose the right '
                                'next step.',
                   'examples': 'A pressure washing estimate page; an HVAC maintenance campaign; a dumpster '
                               'rental inquiry form that collects size and delivery details.',
                   'services': ['local-seo',
                                'google-business-profile',
                                'website-design',
                                'digital-advertising',
                                'lead-automation'],
                   'question': 'Can you market emergency and scheduled services separately?',
                   'answer': 'Yes. We can structure pages and campaigns around the services and availability '
                             'you actually provide.',
                   'description': 'Local SEO & Marketing for Home Service Businesses. Reboot Syndicate helps '
                                  'hvac, plumbing, electrical, pressure washing, cleaning and junk removal '
                                  'companies in Brevard County and remotely.'},
 'retail': {'name': 'Retail & E-Commerce',
            'title': 'E-Commerce Marketing & Website Design for Retailers',
            'headline': 'Help shoppers discover products and complete purchases.',
            'audience': 'Boutiques, specialty stores, gift shops and online brands',
            'challenge': 'Shoppers need useful product details, clear shipping or pickup options and a '
                         'straightforward checkout. Local stores also benefit from accurate hours and '
                         'location information.',
            'examples': 'A product collection for seasonal arrivals; a local pickup landing page; '
                        'permission-based new product emails and checkout measurement.',
            'services': ['ecommerce',
                         'website-design',
                         'social-media',
                         'digital-advertising',
                         'analytics-conversion'],
            'question': 'Can you improve my existing online store?',
            'answer': 'Often, yes. We review your platform, catalog and checkout before recommending changes '
                      'or a migration.',
            'description': 'E-Commerce Marketing & Website Design for Retailers. Reboot Syndicate helps '
                           'boutiques, specialty stores, gift shops and online brands in Brevard County and '
                           'remotely.'},
 'healthcare-wellness': {'name': 'Healthcare & Wellness',
                         'title': 'Website Design & Digital Marketing for Healthcare Practices',
                         'headline': 'Make it easier for patients to discover your practice.',
                         'audience': 'Medical and dental practices, chiropractors, physical therapists, '
                                     'behavioral health practices, med spas and veterinary clinics',
                         'challenge': 'People looking for care need accurate information about providers, '
                                      'specialties, office hours, accessibility and appointment options. '
                                      'Build trust with clear public information and direct visitors to '
                                      'approved scheduling channels without collecting sensitive information '
                                      'in ordinary marketing forms.',
                         'examples': 'A dental practice website with treatment information and a link to its '
                                     'approved booking system; a physical therapy clinic page explaining '
                                     'referral and appointment options; local search updates for a '
                                     'multi-provider practice. Avoid sending patient information to '
                                     'advertising or analytics tools.',
                         'services': ['website-design',
                                      'local-seo',
                                      'google-business-profile',
                                      'content-marketing',
                                      'reputation-management'],
                         'question': 'Can you work with our existing patient scheduling system?',
                         'answer': 'We can review approved public links and supported integrations. Any '
                                   'handling of protected health information requires a separate privacy and '
                                   'security review, appropriate agreements where required, and practice '
                                   'approval. We do not claim blanket HIPAA compliance.',
                         'description': 'Website design, local SEO and digital marketing for medical, '
                                        'dental, therapy and wellness practices in Brevard County, Florida, '
                                        'and remotely.'},
 'professional-services': {'name': 'Professional Services',
                           'title': 'Website Design & Digital Marketing for Professional Services',
                           'headline': 'Turn expertise into a clear reason to choose your firm.',
                           'audience': 'Law firms, accountants, CPAs, insurance agencies, financial '
                                       'advisors, consultants and engineering firms',
                           'challenge': 'Prospective clients compare expertise, credentials, practice areas '
                                        'and responsiveness before booking a consultation. Explain what your '
                                        'firm does, who it serves and how an initial engagement works while '
                                        'respecting professional advertising and confidentiality '
                                        'requirements.',
                           'examples': 'A law firm website organized by practice area; a CPA firm landing '
                                       'page for small-business accounting inquiries; an engineering '
                                       'consultancy portfolio with approved project descriptions; an '
                                       'insurance agency consultation page that avoids collecting sensitive '
                                       'details.',
                           'services': ['website-design',
                                        'local-seo',
                                        'content-marketing',
                                        'branding-design',
                                        'lead-automation'],
                           'question': 'Can you market a regulated professional practice?',
                           'answer': 'We can prepare websites and campaigns for your review, using approved '
                                     'claims and credentials. Your firm must approve material for applicable '
                                     'professional advertising rules, privacy obligations and platform '
                                     'restrictions before publication.',
                           'description': 'Website design, SEO and digital marketing for law firms, '
                                          'accountants, insurance agencies, consultants and other '
                                          'professional services in Brevard County and remotely.'}}
@router.get('/industries')
def industry_overview(request: Request):
    return templates.TemplateResponse(request, 'industries.html', {'industries': INDUSTRIES, 'page': None, 'title': 'Industries We Serve | Reboot Syndicate', 'description': 'Industry-specific website design, SEO and marketing for Space Coast businesses and remote clients.', 'canonical': BASE+'/industries'})
@router.get('/industries/{slug}')
def industry_detail(request: Request, slug: str):
    page = INDUSTRIES.get(slug)
    if page is None:
        raise HTTPException(404, 'Industry not found')
    return templates.TemplateResponse(request, 'industries.html', {'industries': INDUSTRIES, 'page': page, 'slug': slug, 'title': page['title']+' | Reboot Syndicate', 'description': page['description'], 'canonical': BASE+'/industries/'+slug, 'services': [(s, SERVICES[s]['name'], SERVICES[s]['form']) for s in page['services']]})
