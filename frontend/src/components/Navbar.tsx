import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Home, BookOpen, UtensilsCrossed, Calendar, MessageCircle, User, LogOut, Leaf
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/log', icon: UtensilsCrossed, label: 'Log Meal' },
  { to: '/plan', icon: Calendar, label: 'Diet Plan' },
  { to: '/chat', icon: MessageCircle, label: 'Chat' },
  { to: '/profile', icon: User, label: 'Profile' },
]

export function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('nutriagent_token')
    localStorage.removeItem('nutriagent_user')
    navigate('/login')
  }

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-60 bg-white border-r border-gray-100 min-h-screen fixed left-0 top-0 z-20">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-gray-100">
          <div className="w-8 h-8 bg-primary-500 rounded-xl flex items-center justify-center">
            <Leaf size={18} className="text-white" />
          </div>
          <span className="font-bold text-lg text-gray-800">NutriAgent</span>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <Link
              key={to}
              to={to}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                location.pathname === to
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="px-3 pb-5">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 w-full transition-colors"
          >
            <LogOut size={18} />
            Log out
          </button>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 z-20 flex">
        {navItems.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            className={clsx(
              'flex-1 flex flex-col items-center py-2 text-xs font-medium transition-colors',
              location.pathname === to
                ? 'text-primary-600'
                : 'text-gray-400 hover:text-gray-600'
            )}
          >
            <Icon size={20} />
            <span className="mt-0.5">{label}</span>
          </Link>
        ))}
      </nav>
    </>
  )
}
