import { Navigate } from 'react-router-dom'

// wraps a route so it only renders for someone holding a token
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')

  if (!token) {
    // replace: swaps the history entry instead of adding one, so Back
    // doesn't bounce the user straight into the blocked page again
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
