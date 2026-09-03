'use client'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { AlertTriangle, Search, Filter, Eye, CheckCircle } from 'lucide-react'
import api from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e'
}

const TYPE_LABELS: Record<string, string> = {
  drowsiness: '😴 Drowsiness',
  phone_usage: '📱 Phone Usage',
  distraction: '👀 Distraction',
  no_seatbelt: '🪑 No Seatbelt',
  yawning: '🥱 Yawning',
  critical_risk: '⚠ Critical Risk',
  no_face: '👤 No Face',
  emotion: '😠 Emotion Alert',
}

export default function IncidentsPage() {
  const [search, setSearch] = useState('')
  const [severity, setSeverity] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['incidents', search, severity],
    queryFn: () => api.get('/incidents/', {
      params: { limit: 100, severity: severity || undefined }
    }).then(r => r.data),
    refetchInterval: 10_000,
  })

  const incidents = data?.incidents ?? []

  const acknowledge = async (id: number) => {
    await api.post(`/incidents/${id}/acknowledge`)
    refetch()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
          <p className="text-surface-100 text-sm mt-0.5">{data?.total ?? 0} total incidents</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
            <input className="input-field pl-9 w-48" placeholder="Search..." value={search}
              onChange={e => setSearch(e.target.value)} />
          </div>
          <select className="input-field w-36" value={severity} onChange={e => setSeverity(e.target.value)}>
            <option value="">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4">
        {['critical', 'high', 'medium', 'low'].map(sev => {
          const count = incidents.filter((i: any) => i.severity === sev).length
          return (
            <div key={sev} className="glass p-4 text-center">
              <div className="text-2xl font-bold" style={{ color: SEVERITY_COLORS[sev] }}>{count}</div>
              <div className="text-xs text-surface-100 capitalize mt-0.5">{sev}</div>
            </div>
          )
        })}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="glass p-5 animate-pulse h-20" />)}
        </div>
      ) : incidents.length === 0 ? (
        <div className="glass p-12 text-center">
          <AlertTriangle className="w-12 h-12 text-surface-100 mx-auto mb-3" />
          <p className="text-surface-100">No incidents recorded yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {incidents.map((inc: any, idx: number) => (
            <motion.div key={inc.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              className={`glass p-4 flex items-center gap-4 ${inc.acknowledged ? 'opacity-60' : ''}`}>
              {/* Severity indicator */}
              <div className="w-1 self-stretch rounded-full flex-shrink-0"
                style={{ background: SEVERITY_COLORS[inc.severity] ?? '#8b949e' }} />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-white">
                    {TYPE_LABELS[inc.incident_type] ?? inc.incident_type}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ color: SEVERITY_COLORS[inc.severity], background: `${SEVERITY_COLORS[inc.severity]}18` }}>
                    {inc.severity}
                  </span>
                  {inc.acknowledged && (
                    <span className="text-xs text-green-400 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> Acknowledged
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-xs text-surface-100">
                  <span>#{inc.incident_code}</span>
                  {inc.risk_score_at_time && <span>Risk: {inc.risk_score_at_time}%</span>}
                  {inc.head_pose && <span>Head: {inc.head_pose}</span>}
                  <span>{formatDistanceToNow(new Date(inc.occurred_at), { addSuffix: true })}</span>
                </div>
              </div>

              {inc.screenshot_path && (
                <img src={`/captures/${inc.screenshot_path.split('/').pop()}`}
                  alt="capture" className="w-16 h-12 object-cover rounded-lg border border-surface-300" />
              )}

              {!inc.acknowledged && (
                <button onClick={() => acknowledge(inc.id)}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-brand-500 border border-brand-500/30 hover:bg-brand-500/10 transition-colors flex-shrink-0">
                  <Eye className="w-3 h-3" /> Ack
                </button>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
