export async function apiFetch(endpoint: string, options: RequestInit = {}, isRetry = false) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('dropp_token') : null;
  
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const res = await fetch(`/api/v1${endpoint}`, {
      ...options,
      headers,
      credentials: 'include', // Send cookies
      cache: 'no-store'
    });

    // If 401, try to refresh the token silently
    if (res.status === 401 && !isRetry && typeof window !== 'undefined') {
      console.log("Token expired. Refreshing...");
      
      const refreshRes = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include'
      });

      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        localStorage.setItem('dropp_token', refreshData.access_token);
        // Retry the original request
        return apiFetch(endpoint, options, true);
      } else {
        // Refresh failed -> log out
        localStorage.removeItem('dropp_token');
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
          window.location.href = '/login';
        }
      }
    }

    if (!res.ok) {
      const text = await res.text();
      let errorMsg = `HTTP ${res.status}`;
      try {
        const json = JSON.parse(text);
        errorMsg = json.detail || errorMsg;
      } catch (e) {
        errorMsg = text.substring(0, 100) || errorMsg;
      }
      throw new Error(`${res.status}: ${errorMsg}`);
    }

    return await res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') throw new Error('Request timed out');
    throw err;
  }
}
