from app.marketing_services import router as marketing_router
from app.seo import router as seo_router
from app.notifications import send_consultation_alert
import os, sqlite3, secrets, re, time
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Reboot Syndicate", docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')
DB = Path(os.getenv('DATABASE_PATH', '/data/requests.sqlite3'))
DB.parent.mkdir(parents=True, exist_ok=True)
security = HTTPBasic(auto_error=False)

@contextmanager
def db():
    conn = sqlite3.connect(str(DB), timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

with db() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT, device TEXT NOT NULL, issue TEXT NOT NULL, service_area TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'new')''')

@app.get('/health')
def health():
    return {'ok': True}

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, 'index.html', {})

@app.post('/request')
def submit(request: Request, background_tasks: BackgroundTasks, name: str = Form(...), email: str = Form(...), phone: str = Form(''), device: str = Form(...), issue: str = Form(...), service_area: str = Form('Online / Remote'), company_website: str = Form('')):
    if company_website:
        return RedirectResponse('/thanks', status_code=303)
    fields = [name.strip(), email.strip(), phone.strip(), device.strip(), issue.strip(), service_area.strip()]
    name, email, phone, device, issue, service_area = fields
    if not (1 <= len(name) <= 100 and 3 <= len(email) <= 200 and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) and len(phone) <= 40 and 1 <= len(device) <= 120 and 10 <= len(issue) <= 2000 and 1 <= len(service_area) <= 100):
        raise HTTPException(422, 'Please check your request details.')
    received_at = datetime.now(timezone.utc).isoformat()
    with db() as conn:
        cursor = conn.execute('INSERT INTO requests(created_at,name,email,phone,device,issue,service_area) VALUES(?,?,?,?,?,?,?)', (received_at, name, email, phone, device, issue, service_area))
        request_id = cursor.lastrowid
    # The database commit has succeeded. Delivery failures will not lose inquiries.
    background_tasks.add_task(send_consultation_alert, {
        'id': request_id,
        'created_at': received_at,
        'name': name,
        'email': email,
        'phone': phone,
        'service': device,
        'message': issue,
    })
    return RedirectResponse('/thanks', status_code=303)

@app.get('/thanks', response_class=HTMLResponse)
def thanks(request: Request):
    return templates.TemplateResponse(request, 'thanks.html', {})

def require_admin(credentials: HTTPBasicCredentials | None = Depends(security)):
    username, password = os.getenv('ADMIN_USER',''), os.getenv('ADMIN_PASSWORD','')
    if not username or not password or not credentials or not (secrets.compare_digest(credentials.username, username) and secrets.compare_digest(credentials.password, password)):
        raise HTTPException(401, 'Administrator access unavailable or unauthorized', headers={'WWW-Authenticate':'Basic realm="Reboot Syndicate Admin"'})
    return True

@app.get('/admin', response_class=HTMLResponse)
def admin(request: Request, authorized=Depends(require_admin)):
    with db() as conn:
        rows = conn.execute('SELECT * FROM requests ORDER BY id DESC LIMIT 300').fetchall()
    return templates.TemplateResponse(request,'admin.html',{'rows':rows})

@app.post('/admin/{request_id}/status')
def update_status(request_id:int, status: str = Form(...), authorized=Depends(require_admin)):
    if status not in {'new','contacted','scheduled','completed','closed'}:
        raise HTTPException(400,'Invalid status')
    with db() as conn:
        conn.execute('UPDATE requests SET status=? WHERE id=?',(status,request_id))
    return RedirectResponse('/admin',status_code=303)

# Service details retain the site's existing theme and request flow.
SERVICES = {
    "pc-laptop-repair": {"title":"PC & LAPTOP REPAIR","intro":"When your system slows down, refuses to start, or acts up, start with a careful diagnosis instead of guesswork.","bullets":["Startup and boot troubleshooting","Hardware fault assessment","Operating system and software troubleshooting","Laptop and desktop tune-ups"],"image":"repair-workshop.png","device":"Laptop"},
    "wifi-networking": {"title":"WI-FI & NETWORKING","intro":"Dead zones, dropped connections, and unstable routers can disrupt an entire day. We help pinpoint the cause.","bullets":["Wireless coverage troubleshooting","Router and access-point configuration","Home network setup","Ethernet and connectivity diagnostics"],"image":"network-workshop.png","device":"Wi-Fi / Network"},
    "upgrades-builds": {"title":"UPGRADES & BUILDS","intro":"Make the most of your existing hardware or get practical guidance on a fresh build.","bullets":["SSD and memory upgrades","Performance evaluations","PC assembly guidance","Hardware compatibility checks"],"image":"pc-build-workshop.png","device":"Desktop PC"},
    "tech-support": {"title":"TECH SUPPORT","intro":"Help with the everyday technology issues that keep interrupting your work and home life.","bullets":["Printer and peripheral setup","Software and update troubleshooting","New device configuration","General technical assistance"],"image":"tech-support-workshop.png","device":"Other Tech Issue"},
    "data-backups": {"title":"DATA & BACKUPS","intro":"Plan safer backups and storage migrations. Recovery options depend on the condition of the device and are never guaranteed.","bullets":["Backup planning and setup","Storage migrations","Drive health and failure assessment","Data recovery feasibility review"],"image":"backup-workshop.png","device":"Data Backup"},
    "small-business-it": {"title":"SMALL BUSINESS IT","intro":"Practical technology support for small offices, workstations, and the networks they depend on.","bullets":["Workstation and device setup","Small-office networking","Connectivity troubleshooting","Basic IT maintenance planning"],"image":"business-it-workshop.png","device":"Small Business IT"},
}

@app.get('/services/{slug}', response_class=HTMLResponse)
def service_detail(request: Request, slug: str):
    service = SERVICES.get(slug)
    if service is None:
        raise HTTPException(404, 'Service not found')
    return templates.TemplateResponse(request, 'service.html', {'service':service})


@app.get('/marketing', response_class=HTMLResponse)
def marketing_page(request: Request):
    return templates.TemplateResponse(request, 'marketing.html', {})

app.include_router(marketing_router)
app.include_router(seo_router)
