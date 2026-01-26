from fastapi import APIRouter
from core.config import settings
from fastapi.responses import RedirectResponse

import urllib.parse


router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.get("/google")
def login_via_google():
    params = {
        "client_id": settings.google.client_id,
        "redirect_uri": settings.google.redirect_uri,
        "response_type": settings.google.response_type,
        "scope": settings.google.scope,
        "access_type": settings.google.access_type,
    }
    url = settings.google.authorize_url + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)
