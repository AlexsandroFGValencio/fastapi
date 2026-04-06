from typing import Optional
from fastapi import Cookie, HTTPException, Request
from fastapi.responses import RedirectResponse

async def get_current_user_web(request: Request, access_token: Optional[str] = Cookie(None)):
    """Get current user from cookie for web routes"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Store token in request state for API calls
    request.state.access_token = access_token
    
    # Get user from session/cookie
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return user_data

def require_auth(func):
    """Decorator to require authentication for web routes"""
    async def wrapper(request: Request, *args, **kwargs):
        access_token = request.cookies.get("access_token")
        if not access_token:
            return RedirectResponse(url="/login", status_code=302)
        
        user_data = request.session.get("user")
        if not user_data:
            return RedirectResponse(url="/login", status_code=302)
        
        return await func(request, *args, **kwargs)
    return wrapper
