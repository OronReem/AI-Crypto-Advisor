// Vite swaps VITE_* in at build time; Vercel supplies the Render URL, the
// fallback keeps `npm run dev` working. Exported because signup and login
// call the backend without a token, so they can't use authFetch.
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export async function authFetch(path, options = {}) {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  })

  // ProtectedRoute only checks a token exists — it can't tell a valid one
  // from an expired one, since verifying the signature needs the server's
  // secret. A 401 is the server telling us this token is no longer good.
  if (response.status === 401) {
    localStorage.removeItem('token')
    // a full page load, not React Router — this runs outside any component,
    // so there's no navigate() available here
    window.location.href = '/login'
  }

  return response
}
