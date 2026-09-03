'use client'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Car, Users, Activity, Wrench, MapPin, Wifi } from 'lucide-react'
import api from '@/lib/api'
import Link from 'next/link'

const STATUS_STYLES: Record<string, string> = {
  active: 'text-green-400 bg-green-500/10 border-green-500/30',
  maintenance: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  inactive: 'text-gray-400 bg-gray-500/10 border-gray-500/30',
  retired: 'text-red-400 bg-red-500/10 border-red-500/30',
}

export default function FleetPage() {
  const { data: overview } = useQuery({
    queryKey: ['fleet-overview'],
    queryFn: () => api.get('/fleet/overview').then(r => r.data),
    refetchInterval: 15_000,
  })

  const { data: liveData } = useQuery({
    queryKey: ['fleet-live'],
    queryFn: () => api.get('/fleet/live').then(r => r.data),
    refetchInterval: 10_000,
  })

  const { data: vehiclesData } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => api.get('/vehicles/', { params: { limit: 100 } }).then(r => r.data),
  })

  const vehicles = vehiclesData?.vehicles ?? []
  const live: any[] = liveData ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Fleet Management</h1>
        <p className="text-surface-100 text-sm mt-0.5">All vehicles and real-time tracking</p>
      </div>

      {/* Overview stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { label: 'Drivers',     value: overview.total_drivers,       icon: Users,    color: '#00c8ff' },
            { label: 'Active',      value: overview.active_drivers,      icon: Activity, color: '#22c55e' },
            { label: 'Vehicles',    value: overview.total_vehicles,      icon: Car,      color: '#7c3aed' },
            { label: 'On Road',     value: overview.active_vehicles,     icon: MapPin,   color: '#22c55e' },
            { label: 'Maintenance', value: overview.maintenance_vehicles,icon: Wrench,   color: '#eab308' },
            { label: 'Live Trips',  value: overview.active_trips,        icon: Wifi,     color: '#f97316' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="glass p-4 text-center">
              <Icon className="w-5 h-5 mx-auto mb-2" style={{ color }} />
              <div className="text-xl font-bold text-white">{value}</div>
              <div className="text-xs text-surface-100">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Live active trips */}
      {live.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Live Trips ({live.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {live.map((trip) => (
              <motion.div key={trip.trip_id} whileHover={{ y: -2 }} className="glass p-4 border border-green-500/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-xl bg-green-500/10">
                    <Car className="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">{trip.driver.name}</div>
                    <div className="text-xs text-surface-100">{trip.driver.employee_id}</div>
                  </div>
                </div>
                {trip.vehicle && (
                  <div className="text-xs text-surface-100 mb-1">
                    🚗 {trip.vehicle.plate} — {trip.vehicle.make} {trip.vehicle.model}
                  </div>
                )}
                <div className="text-xs text-surface-100">
                  📍 {trip.start_location || 'Unknown location'}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Vehicles table */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3">All Vehicles ({vehicles.length})</h2>
        <div className="glass overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-300">
                  {['Plate', 'Make/Model', 'Year', 'Status', 'Camera', 'GPS', 'Odometer'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-surface-100">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {vehicles.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-surface-100 text-sm">
                      No vehicles registered yet.
                    </td>
                  </tr>
                ) : vehicles.map((v: any) => (
                  <tr key={v.id} className="border-b border-surface-300/30 hover:bg-surface-700/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-brand-500 font-medium">{v.plate_number}</td>
                    <td className="px-4 py-3 text-white">{v.make} {v.model}</td>
                    <td className="px-4 py-3 text-surface-100">{v.year}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${STATUS_STYLES[v.status] ?? ''}`}>
                        {v.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={v.camera_installed ? 'text-green-400' : 'text-red-400'}>
                        {v.camera_installed ? '✓' : '✗'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={v.gps_enabled ? 'text-green-400' : 'text-red-400'}>
                        {v.gps_enabled ? '✓' : '✗'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-surface-100">{v.odometer_km?.toFixed(0) ?? 0} km</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
