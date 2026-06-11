import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, Target, Megaphone, Coffee } from 'lucide-react'
import { cn } from '../lib/utils'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/segments', label: 'Segments', icon: Target },
  { to: '/campaigns', label: 'Campaigns', icon: Megaphone },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-60 flex-col border-r border-gray-200 bg-gray-50">
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6">
        <Coffee className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-lg font-bold text-gray-900">XenoCRM</h1>
          <p className="text-xs text-gray-500">BrewCo</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-gray-200 p-4">
        <p className="text-xs text-gray-400">AI-native Mini CRM</p>
      </div>
    </aside>
  )
}
