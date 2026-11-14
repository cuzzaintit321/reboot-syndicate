from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.ai_catalog import AI
router=APIRouter()
templates=Jinja2Templates(directory='app/templates')
@router.get('/ai-solutions')
def solutions(request: Request):
    return templates.TemplateResponse(request,'ai_solutions.html',{'services':AI})
@router.get('/ai-readiness')
def readiness(request: Request):
    return templates.TemplateResponse(request,'ai_readiness.html',{})
