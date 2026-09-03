'use client'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'
import { User, Mail, Phone, Shield, Calendar, LogOut, Key } from 'lucide-react'
import { format } from 'date-fns'

export default function SettingsPage() {
  const { user, logout } = useAuth()

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-surface-100 text-sm mt-0.5">Account & preferences</p>
      </div>

      {/* Profile card */}
      <div className="glass p-6">
        <h2 className="font-semibold text-white mb-5 flex items-center gap-2">
          <User className="w-4 h-4 text-brand-500" /> Profile
        </h2>
        <div className="flex items-center gap-5 mb-6">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold"
            style={{ background: 'linear-gradient(135deg,rgba(0,200,255,0.3),rgba(0,100,200,0.3))', border: '1px solid rgba(0,200,255,0.3)' }}>
            {user?.full_name?.charAt(0) ?? '?'}
          </div>
          <div>
            <div className="text-lg font-bold text-white">{user?.full_name}</div>
            <div className="text-sm text-surface-100">@{user?.username}</div>
            <div className="mt-1 px-2 py-0.5 rounded-full text-xs font-medium bg-brand-500/10 text-brand-500 border border-brand-500/30 inline-block">
              {user?.role?.replace('_', ' ').toUpperCase()}
            </div>
          </div>
        </div>

        <div className="space-y-3">
          {[
            { icon: Mail,     label: 'Email',    value: user?.email },
            { icon: Phone,    label: 'Phone',    value: user?.phone || '—' },
            { icon: Shield,   label: 'Role',     value: user?.role },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'rgba(13,17,23,0.6)' }}>
              <Icon className="w-4 h-4 text-surface-100" />
              <span className="text-xs text-surface-100 w-16">{label}</span>
              <span className="text-sm text-white">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* AI Modules config */}
      <div className="glass p-6">
        <h2 className="font-semibold text-white mb-5 flex items-center gap-2">
          <Key className="w-4 h-4 text-brand-500" /> AI Module Settings
        </h2>
        <div className="space-y-3">
          {[
            { label: 'Face Detection',    desc: 'MediaPipe face detection',           default: true },
            { label: 'Eye Tracking',      desc: 'EAR-based eye state detection',      default: true },
            { label: 'Drowsiness Alert',  desc: 'Extended eye closure detection',     default: true },
            { label: 'Head Pose',         desc: 'Pitch / yaw / roll estimation',      default: true },
            { label: 'Yawn Detection',    desc: 'MAR-based mouth aspect ratio',       default: true },
            { label: 'Phone Detection',   desc: 'YOLOv8 cell phone detection',        default: true },
            { label: 'Voice Alerts',      desc: 'Text-to-speech safety warnings',     default: true },
            { label: 'Screenshot Capture',desc: 'Auto-capture on incident events',    default: true },
          ].map(({ label, desc, default: def }) => (
            <div key={label} className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'rgba(13,17,23,0.6)' }}>
              <div>
                <div className="text-sm font-medium text-white">{label}</div>
                <div className="text-xs text-surface-100">{desc}</div>
              </div>
              <div className="relative">
                <input type="checkbox" defaultChecked={def} className="sr-only peer" id={label} />
                <label htmlFor={label}
                  className="w-10 h-5 bg-surface-300 rounded-full cursor-pointer relative block peer-checked:bg-brand-500 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-4 after:h-4 after:rounded-full after:bg-white after:transition-transform peer-checked:after:translate-x-5" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Danger zone */}
      <div className="glass p-6 border border-red-500/20">
        <h2 className="font-semibold text-white mb-4">Account Actions</h2>
        <button onClick={logout}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-400 border border-red-500/30 bg-red-500/5 hover:bg-red-500/15 transition-colors">
          <LogOut className="w-4 h-4" /> Sign Out
        </button>
      </div>
    </div>
  )
}
