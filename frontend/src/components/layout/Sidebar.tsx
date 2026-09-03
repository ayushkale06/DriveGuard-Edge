'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Camera, BarChart2, Car, Users,
  AlertTriangle, Activity, Settings, Shield, ChevronLeft,
  ChevronRight, Truck
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const NAV = [
  { href: '/dashboard',             label: 'Dashboard',    icon: LayoutDashboard },
  { href: '/dashboard/monitoring',  label: 'Live Monitor', icon: Camera,         badge: 'LIVE' },
  { href: '/dashboard/analytics',   label: 'Analytics',    icon: BarChart2 },
  { href: '/dashboard/trips',       label: 'Trips',        icon: Activity },
  { href: '/dashboard/incidents',   label: 'Incidents',    icon: AlertTriangle },
  { href: '/dashboard/drivers',     label: 'Drivers',      icon: Users },
  { href: '/dashboard/fleet',       label: 'Fleet',        icon: Truck },
  { href: '/dashboard/settings',    label: 'Settings',     icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 220 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="flex-shrink-0 h-screen flex flex-col border-r border-surface-300/50 overflow-hidden"
      style={{ background: 'rgba(13,17,23,0.98)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-surface-300/30">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 glow-brand"
          style={{ background: 'linear-gradient(135deg,rgba(0,200,255,0.25),rgba(0,100,200,0.35))', border: '1px solid rgba(0,200,255,0.35)' }}>
          <Shield className="w-5 h-5 text-brand-500" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }}
              className="overflow-hidden">
              <div className="text-sm font-bold text-white leading-tight">DriveGuard</div>
              <div className="text-xs text-brand-500 font-medium">Edge v2.0</div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {NAV.map(({ href, label, icon: Icon, badge }) => {
          const active = href === '/dashboard' ? pathname === href : pathname.startsWith(href)
          return (
            <Link key={href} href={href}
              className={cn('sidebar-link', active && 'active', collapsed && 'justify-center px-0')}
              title={collapsed ? label : undefined}>
              <Icon className="w-4.5 h-4.5 flex-shrink-0 w-[18px] h-[18px]" />
              <AnimatePresence>
                {!collapsed && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex-1 flex items-center justify-between">
                    {label}
                    {badge && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                        {badge}
                      </span>
                    )}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <button onClick={() => setCollapsed(c => !c)}
        className="flex items-center justify-center h-10 border-t border-surface-300/30 text-surface-100 hover:text-white hover:bg-surface-700/30 transition-colors">
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </motion.aside>
  )
}
