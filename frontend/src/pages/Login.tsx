import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register, login } from '../api'
import toast from 'react-hot-toast'
import { LoadingSpinner } from '../components/LoadingState'
import { Leaf } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', name: '' })

  function update(k: string, v: string) {
    setForm(f => ({ ...f, [k]: v }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const data = mode === 'login'
        ? await login(form.email, form.password)
        : await register(form.email, form.password, form.name)

      localStorage.setItem('nutriagent_token', data.access_token)
      localStorage.setItem('nutriagent_user', JSON.stringify({ id: data.user_id, name: data.name }))

      toast.success(mode === 'login' ? `Welcome back, ${data.name}!` : 'Account created!')
      navigate(mode === 'register' ? '/onboarding' : '/')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-soft w-full max-w-sm p-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 bg-primary-500 rounded-xl flex items-center justify-center">
            <Leaf size={18} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-gray-800 text-lg leading-tight">NutriAgent</h1>
            <p className="text-xs text-gray-400">AI Nutrition Platform</p>
          </div>
        </div>

        <h2 className="text-xl font-bold text-gray-800 mb-1">
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </h2>
        <p className="text-sm text-gray-500 mb-5">
          {mode === 'login' ? 'Welcome back! Enter your credentials.' : 'Start your nutrition journey.'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="label">Full Name</label>
              <input
                className="input" type="text" required
                placeholder="Your name"
                value={form.name} onChange={e => update('name', e.target.value)}
              />
            </div>
          )}
          <div>
            <label className="label">Email</label>
            <input
              className="input" type="email" required
              placeholder="you@example.com"
              value={form.email} onChange={e => update('email', e.target.value)}
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input" type="password" required minLength={6}
              placeholder="••••••••"
              value={form.password} onChange={e => update('password', e.target.value)}
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading && <LoadingSpinner size={16} />}
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => setMode(m => m === 'login' ? 'register' : 'login')}
            className="text-primary-600 font-medium hover:underline"
          >
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>

        {/* Demo note */}
        
      </div>
    </div>
  )
}
