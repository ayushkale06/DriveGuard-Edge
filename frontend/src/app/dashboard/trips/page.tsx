'use client'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Activity, Clock, Map, Car, Users, ChevronRight } from 'lucide-react'
import api from '@/lib/api'
import { formatDuration, getRiskColor } from '@/lib/utils'
import { formatDistanceToNow, format } from 'date-fns'

const STATUS_COLORS: Record<string, string> = {
  active: '#22c55e', completed: '#8b949e', cancelled: '#ef4444', paused: '#eab308'
}

export default function TripsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['trips'],
    queryFn: () => api.get('/trips/', { params: { limit: 100 } }).then(r => r.data),
    refetchInterval: 15_000,
  })

  const trips = data?.trips ?? []
  const active = trips.filter((t: any) => t.status === 'active')
  const completed = trips.filter((t: any) => t.status === 'completed')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Trip History</h1>
          <p className="text-surface-100 text-sm mt-0.5">{data?.total ?? 0} total trips</p>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total',     value: data?.total ?? 0,    color: '#00c8ff' },
          { label: 'Active',    value: active.length,       color: '#22c55e' },
          { label: 'Completed', value: completed.length,    color: '#8b949e' },
          { label: 'Cancelled', value: trips.filter((t:any) => t.status==='cancelled').length, color: '#ef4444' },
        ].map(({ label, value, color }) => (
          <div key={label} className="glass p-4 text-center">
            <div className="text-2xl font-bold" style={{ color }}>{value}</div>
            <div className="text-xs text-surface-100 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Active trips */}
      {active.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Active Trips ({active.length})
          </h2>
          <div className="space-y-2">
            {active.map((trip: any) => (
              <div key={trip.id} className="glass p-4 flex items-center gap-4 border border-green-500/20">
                <div className="p-2.5 rounded-xl bg-green-500/10">
                  <Car className="w-4 h-4 text-green-400" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-white text-sm">{trip.trip_code}</div>
                  <div className="text-xs text-surface-100">
                    Started {formatDistanceToNow(new Date(trip.start_time), { addSuffix: true })}
                    {trip.start_location && ` · ${trip.start_location}`}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold" style={{ color: getRiskColor(trip.average_risk_score) }}>
                    {trip.average_risk_score?.toFixed(0)}% risk
                  </div>
                  <div className="text-xs text-surface-100">{formatDuration(trip.duration_seconds || 0)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All trips table */}
      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-300">
                {['Trip Code', 'Status', 'Duration', 'Distance', 'Risk Score', 'Blinks', 'Incidents', 'Started'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-surface-100">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-surface-300/50">
                    {[...Array(8)].map((_, j) => (
                      <td key={j} className="px-4 py-3"><div className="h-4 bg-surface-600 rounded animate-pulse w-16" /></td>
                    ))}
                  </tr>
                ))
              ) : trips.map((trip: any) => (
                <tr key={trip.id} className="border-b border-surface-300/30 hover:bg-surface-700/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-brand-500 text-xs">{trip.trip_code}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium"
                      style={{ color: STATUS_COLORS[trip.status], background: `${STATUS_COLORS[trip.status]}18` }}>
                      {trip.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-white">{formatDuration(trip.duration_seconds || 0)}</td>
                  <td className="px-4 py-3 text-surface-100">{trip.distance_km?.toFixed(1) ?? '—'} km</td>
                  <td className="px-4 py-3">
                    <span style={{ color: getRiskColor(trip.average_risk_score) }} className="font-medium">
                      {trip.average_risk_score?.toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-white">{trip.total_blinks ?? 0}</td>
                  <td className="px-4 py-3 text-white">{(trip.drowsy_events + trip.phone_events + trip.distraction_events) || 0}</td>
                  <td className="px-4 py-3 text-surface-100 text-xs">
                    {format(new Date(trip.start_time), 'MMM d, HH:mm')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
