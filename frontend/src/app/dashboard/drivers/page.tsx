'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Users, Plus, Search, Phone, Mail, Shield, ChevronRight, X } from 'lucide-react'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import Link from 'next/link'

interface Driver {
  id: number
  employee_id: string
  full_name: string
  email: string
  phone?: string
  license_number?: string
  total_trips: number
  total_incidents: number
  average_risk_score: number
  safety_rating: number
  is_active: boolean
  created_at: string
}

function RiskBadge({ score }: { score: number }) {
  const color = score >= 85 ? 'text-green-400 bg-green-500/10 border-green-500/30' :
                score >= 65 ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30' :
                'text-red-400 bg-red-500/10 border-red-500/30'
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {score.toFixed(0)}%
    </span>
  )
}

function AddDriverModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ employee_id: '', full_name: '', email: '', phone: '' })
  const mutation = useMutation({
    mutationFn: (data: typeof form) => api.post('/drivers/', data).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['drivers'] }); toast.success('Driver added'); onClose() },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Failed to add driver'),
  })
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="glass p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-white">Add Driver</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-surface-100 hover:text-white" /></button>
        </div>
        <div className="space-y-4">
          {[
            { label: 'Employee ID', key: 'employee_id', placeholder: 'EMP-001' },
            { label: 'Full Name',   key: 'full_name',   placeholder: 'John Doe' },
            { label: 'Email',       key: 'email',       placeholder: 'john@example.com' },
            { label: 'Phone',       key: 'phone',       placeholder: '+1 555 000 0000' },
          ].map(({ label, key, placeholder }) => (
            <div key={key}>
              <label className="text-xs text-surface-100 mb-1 block">{label}</label>
              <input className="input-field" placeholder={placeholder}
                value={(form as any)[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} />
            </div>
          ))}
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="flex-1 py-2 rounded-xl text-sm text-surface-100 border border-surface-300 hover:border-surface-200">Cancel</button>
          <button className="flex-1 btn-primary" onClick={() => mutation.mutate(form)} disabled={mutation.isPending}>
            {mutation.isPending ? 'Adding...' : 'Add Driver'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default function DriversPage() {
  const [search, setSearch] = useState('')
  const [showAdd, setShowAdd] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['drivers', search],
    queryFn: () => api.get('/drivers/', { params: { search: search || undefined, limit: 100 } }).then(r => r.data),
  })

  const drivers: Driver[] = data?.drivers ?? []

  return (
    <div className="space-y-6">
      {showAdd && <AddDriverModal onClose={() => setShowAdd(false)} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Driver Profiles</h1>
          <p className="text-surface-100 text-sm mt-0.5">{data?.total ?? 0} registered drivers</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" /> Add Driver
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
        <input className="input-field pl-9" placeholder="Search drivers..." value={search}
          onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass p-5 animate-pulse h-40" />
          ))}
        </div>
      ) : drivers.length === 0 ? (
        <div className="glass p-12 text-center">
          <Users className="w-12 h-12 text-surface-100 mx-auto mb-3" />
          <p className="text-surface-100">No drivers found. Add your first driver!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {drivers.map((d) => (
            <motion.div key={d.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -3 }} className="glass glass-hover p-5 cursor-pointer">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-full flex items-center justify-center text-lg font-bold"
                    style={{ background: 'linear-gradient(135deg, rgba(0,200,255,0.3), rgba(0,100,200,0.3))', border: '1px solid rgba(0,200,255,0.3)' }}>
                    {d.full_name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-semibold text-white text-sm">{d.full_name}</div>
                    <div className="text-xs text-surface-100">{d.employee_id}</div>
                  </div>
                </div>
                <div className={`w-2 h-2 rounded-full ${d.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
              </div>

              <div className="grid grid-cols-3 gap-2 mb-4">
                {[
                  { label: 'Trips',     value: d.total_trips },
                  { label: 'Incidents', value: d.total_incidents },
                  { label: 'Rating',    value: d.safety_rating.toFixed(1) },
                ].map(({ label, value }) => (
                  <div key={label} className="text-center">
                    <div className="text-base font-bold text-white">{value}</div>
                    <div className="text-xs text-surface-100">{label}</div>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between">
                <RiskBadge score={d.average_risk_score} />
                <div className="flex items-center gap-1 text-xs text-surface-100">
                  <Mail className="w-3 h-3" />
                  <span className="truncate max-w-[120px]">{d.email}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
