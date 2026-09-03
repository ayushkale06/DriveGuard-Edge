'use client'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Users, Car, AlertTriangle, Activity, TrendingUp,
  Shield, Zap, Eye, ChevronRight, ArrowUpRight
} from 'lucide-react'
import api from '@/lib/api'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { getRiskColor, formatDuration } from '@/lib/utils'
import Link from 'next/link'

const StatCard = ({ icon: Icon, label, value, sub, color, href }: any) => (
  <Link href={href || '#'}>
    <motion.div
      whileHover={{ y: -4 }}
      className="glass glass-hover p-5 cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="p-2.5 rounded-xl" style={{ background: `${color}18`, border: `1px solid ${color}30` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        <ArrowUpRight className="w-4 h-4 text-surface-100" />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-sm text-surface-100 mt-0.5">{label}</div>
      {sub && <div className="text-xs mt-1" style={{ color }}>{sub}</div>}
    </motion.div>
  </Link>
)

const INCIDENT_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#00c8ff', '#7c3aed']

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/analytics/dashboard').then(r => r.data),
    refetchInterval: 15_000,
  })

  const stats = [
    { icon: Users,         label: 'Total Drivers',   value: data?.total_drivers ?? '—',   sub: `${data?.active_drivers ?? 0} active`,    color: '#00c8ff', href: '/dashboard/drivers' },
    { icon: Car,           label: 'Fleet Vehicles',  value: data?.total_vehicles ?? '—',  sub: `${data?.active_trips ?? 0} on road`,     color: '#22c55e', href: '/dashboard/fleet' },
    { icon: Activity,      label: "Today's Trips",   value: data?.today_trips ?? '—',      sub: `${data?.total_trips ?? 0} total`,        color: '#7c3aed', href: '/dashboard/trips' },
    { icon: AlertTriangle, label: "Today's Incidents", value: data?.today_incidents ?? '—', sub: `${data?.total_incidents ?? 0} all time`, color: '#ef4444', href: '/dashboard/incidents' },
    { icon: Shield,        label: 'Fleet Risk Score', value: data ? `${data.average_fleet_risk}%` : '—', sub: 'Fleet average', color: '#eab308', href: '/dashboard/analytics' },
    { icon: Zap,           label: 'Active Sessions', value: data?.active_trips ?? '—',    sub: 'Live monitoring',                         color: '#f97316', href: '/dashboard/monitoring' },
  ]

  const trendData = data?.trips_trend ?? []
  const incidentTypes = data?.incident_types ?? []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Fleet Dashboard</h1>
          <p className="text-surface-100 text-sm mt-0.5">Real-time monitoring overview</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium text-green-400 border border-green-500/30 bg-green-500/10">
          <span className="relative w-2 h-2">
            <span className="live-dot relative flex h-2 w-2 rounded-full bg-green-400" />
          </span>
          LIVE
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trips Trend */}
        <div className="lg:col-span-2 glass p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Trips — Last 7 Days</h2>
            <Link href="/dashboard/trips" className="text-brand-500 text-xs flex items-center gap-1 hover:underline">
              View all <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trendData.length ? trendData : Array(7).fill(0).map((_, i) => ({ date: `Day ${i+1}`, trips: 0 }))}>
              <defs>
                <linearGradient id="tripGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#00c8ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00c8ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
              <Area type="monotone" dataKey="trips" stroke="#00c8ff" strokeWidth={2} fill="url(#tripGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Incident Types */}
        <div className="glass p-5">
          <h2 className="font-semibold text-white mb-4">Incident Breakdown</h2>
          {incidentTypes.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={incidentTypes} dataKey="count" nameKey="type" cx="50%" cy="50%" outerRadius={65} innerRadius={35}>
                    {incidentTypes.map((_: any, i: number) => (
                      <Cell key={i} fill={INCIDENT_COLORS[i % INCIDENT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 mt-2">
                {incidentTypes.slice(0, 4).map((item: any, i: number) => (
                  <div key={item.type} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ background: INCIDENT_COLORS[i % INCIDENT_COLORS.length] }} />
                      <span className="text-surface-100 capitalize">{item.type.replace('_', ' ')}</span>
                    </div>
                    <span className="text-white font-medium">{item.count}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-40 text-surface-100 text-sm">No incident data yet</div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Live Monitoring', href: '/dashboard/monitoring', icon: Eye,    color: '#00c8ff', desc: 'Real-time AI camera' },
          { label: 'Trip Reports',   href: '/dashboard/trips',       icon: Activity, color: '#22c55e', desc: 'History & analytics' },
          { label: 'Fleet View',     href: '/dashboard/fleet',       icon: Car,     color: '#7c3aed', desc: 'All vehicles & drivers' },
          { label: 'Incidents',      href: '/dashboard/incidents',   icon: AlertTriangle, color: '#ef4444', desc: 'Safety events' },
        ].map(({ label, href, icon: Icon, color, desc }) => (
          <Link key={href} href={href}>
            <motion.div whileHover={{ y: -3 }} className="glass glass-hover p-4 cursor-pointer">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg" style={{ background: `${color}18` }}>
                  <Icon className="w-4 h-4" style={{ color }} />
                </div>
                <span className="text-sm font-semibold text-white">{label}</span>
              </div>
              <p className="text-xs text-surface-100">{desc}</p>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  )
}
