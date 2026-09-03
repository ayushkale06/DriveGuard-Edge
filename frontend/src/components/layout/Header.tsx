'use client'
import { useAuth } from '@/contexts/AuthContext'
import { Bell, Search, LogOut, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export default function Header() {
  const { user, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  const { data: alerts } = useQuery({
    queryKey: ['unread-alerts'],
    queryFn: () => api.get('/incidents/alerts/unread').then(r => r.data).catch(() => []),
    refetchInterval: 30_000,
  })

  const unread = Array.isArray(alerts) ? alerts.length : 0

  return (
    <header className="flex items-center justify-between px-6 h-14 border-b border-surface-300/30 flex-shrink-0"
      style={{ background: 'rgba(13,17,23,0.98)' }}>
      {/* Search */}
      <div className="relative hidden md:block">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
        <input className="input-field pl-9 w-56 h-8 text-xs" placeholder="Search..." />
      </div>

      <div className="flex items-center gap-3 ml-auto">
        {/* Notifications */}
        <button className="relative p-2 rounded-xl text-surface-100 hover:text-white hover:bg-surface-700/40 transition-colors">
          <Bell className="w-4 h-4" />
          {unread > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </button>

        {/* User menu */}
        <div className="relative">
          <button onClick={() => setMenuOpen(o => !o)}
            className="flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-xl hover:bg-surface-700/40 transition-colors">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold"
              style={{ background: 'linear-gradient(135deg,rgba(0,200,255,0.3),rgba(0,100,200,0.4))' }}>
              {user?.full_name?.charAt(0) ?? '?'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-medium text-white leading-tight">{user?.full_name?.split(' ')[0]}</div>
              <div className="text-[10px] text-surface-100 capitalize">{user?.role?.replace('_', ' ')}</div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-surface-100" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 glass py-1 z-50 shadow-xl">
              <div className="px-3 py-2 border-b border-surface-300/30">
                <div className="text-xs font-medium text-white">{user?.full_name}</div>
                <div className="text-xs text-surface-100">{user?.email}</div>
              </div>
              <button onClick={logout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors">
                <LogOut className="w-4 h-4" /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
