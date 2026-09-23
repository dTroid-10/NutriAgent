import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Navbar } from './components/Navbar'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import LogMeal from './pages/LogMeal'
import DietPlan from './pages/DietPlan'
import Chat from './pages/Chat'
import Profile from './pages/Profile'

function isAuthenticated() {
  return Boolean(localStorage.getItem('nutriagent_token'))
}

function PrivateRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Navbar />
      {/* Main content */}
      <main className="flex-1 md:ml-60 p-4 md:p-6 pb-24 md:pb-6 max-w-5xl w-full">
        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            borderRadius: '12px',
            fontSize: '13px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#fff' } },
        }}
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/onboarding" element={
          isAuthenticated() ? <Onboarding /> : <Navigate to="/login" replace />
        } />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/log" element={<PrivateRoute><LogMeal /></PrivateRoute>} />
        <Route path="/plan" element={<PrivateRoute><DietPlan /></PrivateRoute>} />
        <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
