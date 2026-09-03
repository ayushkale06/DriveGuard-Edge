'use client'
import { useQuery } from '@tanstack/react-query'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line } from 'recharts'
import api from '@/lib/api'
import { getRiskColor } from '@/lib/utils'
import { TrendingUp, Activity, Shield } from 'lucide-react'

export default function AnalyticsPage() {
  const { data: dashboard } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => api.get('/analytics/dashboard').then(r => r.data),
    refetchInterval: 30_000,
  })

  const { data: riskTimeline } = useQuery({
    queryKey: ['risk-timeline'],
    queryFn: () => api.get('/analytics/risk-timeline', { params: { hours: 1 } }).then(r => r.data),
    refetchInterval: 10_000,
  })

  const timelineData = (riskTimeline ?? []).map((d: any) => ({
    time: new Date(d.timestamp).toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
    risk: d.risk_score,
    ear: Math.round(d.ear * 100),
    blinks: d.blinks,
  })).slice(-60)

  const incidentData = (dashboard?.incident_types ?? []).map((d: any) => ({
    name: d.type.replace('_', ' '),
    count: d.count,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-surface-100 text-sm mt-0.5">Fleet-wide performance metrics</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Avg Fleet Risk',    value: `${dashboard?.average_fleet_risk ?? 100}%`, color: getRiskColor(dashboard?.average_fleet_risk ?? 100), icon: Shield },
          { label: 'Total Trips',       value: dashboard?.total_trips ?? 0,                color: '#00c8ff',                                           icon: Activity },
          { label: 'Total Incidents',   value: dashboard?.total_incidents ?? 0,            color: '#ef4444',                                           icon: TrendingUp },
          { label: "Today's Incidents", value: dashboard?.today_incidents ?? 0,            color: '#f97316',                                           icon: TrendingUp },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="glass p-5">
            <div className="flex items-center gap-3 mb-2">
              <Icon className="w-4 h-4" style={{ color }} />
              <span className="text-xs text-surface-100">{label}</span>
            </div>
            <div className="text-3xl font-bold" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Risk Timeline */}
      <div className="glass p-5">
        <h2 className="font-semibold text-white mb-4">Risk Score — Last Hour</h2>
        {timelineData.length > 1 ? (
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={timelineData}>
              <defs>
                <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="time" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
              <Area type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} fill="url(#riskGrad)" name="Risk %" />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-40 flex items-center justify-center text-surface-100 text-sm">
            No live monitoring data. Start a monitoring session to see data here.
          </div>
        )}
      </div>

      {/* Two-col charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trips per day */}
        <div className="glass p-5">
          <h2 className="font-semibold text-white mb-4">Trips — Last 7 Days</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dashboard?.trips_trend ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="date" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="trips" fill="#00c8ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Incident breakdown */}
        <div className="glass p-5">
          <h2 className="font-semibold text-white mb-4">Incident Types</h2>
          {incidentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={incidentData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} width={90} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-surface-100 text-sm">No incident data yet</div>
          )}
        </div>
      </div>

      {/* EAR / Blink charts */}
      {timelineData.length > 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass p-5">
            <h2 className="font-semibold text-white mb-4">EAR (Eye Aspect Ratio × 100)</h2>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="time" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="ear" stroke="#00c8ff" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="glass p-5">
            <h2 className="font-semibold text-white mb-4">Blink Count Over Time</h2>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={timelineData}>
                <defs>
                  <linearGradient id="blinkGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#7c3aed" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="time" tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
                <Area type="monotone" dataKey="blinks" stroke="#7c3aed" fill="url(#blinkGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
