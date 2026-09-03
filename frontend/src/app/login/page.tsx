'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Shield, Eye, Zap, Car, Lock, Mail, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Link from 'next/link'

export default function LoginPage() {
  const { login } = useAuth()
  const router = useRouter()
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ identifier: '', password: '', email: '', username: '', full_name: '' })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.identifier, form.password)
      toast.success('Welcome back!')
      router.push('/dashboard')
    } catch {
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/auth/register', {
        email: form.email,
        username: form.username,
        full_name: form.full_name,
        password: form.password,
        role: 'driver',
      })
      toast.success('Account created! Please log in.')
      setTab('login')
      setForm(f => ({ ...f, identifier: form.username }))
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-animated flex items-center justify-center p-4">
      {/* Background particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-brand-500 rounded-full opacity-20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float ${3 + Math.random() * 4}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 glow-brand"
               style={{ background: 'linear-gradient(135deg, rgba(0,200,255,0.2), rgba(0,102,204,0.3))', border: '1px solid rgba(0,200,255,0.3)' }}>
            <Shield className="w-10 h-10 text-brand-500" />
          </div>
          <h1 className="text-3xl font-bold gradient-text">DriveGuard Edge</h1>
          <p className="text-surface-100 mt-1 text-sm">AI Powered Driver Monitoring Platform</p>
        </div>

        {/* Card */}
        <div className="glass p-8">
          {/* Tabs */}
          <div className="flex rounded-xl p-1 mb-6" style={{ background: 'rgba(13,17,23,0.8)' }}>
            {(['login', 'register'] as const).map(t => (
              <button key={t} onClick={() => setTab(t)}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${tab === t ? 'bg-brand-500 text-white' : 'text-surface-100 hover:text-white'}`}>
                {t === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Email or Username</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
                  <input className="input-field pl-9" placeholder="admin@driveguard.com" required
                    value={form.identifier} onChange={e => setForm(f => ({ ...f, identifier: e.target.value }))} />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
                  <input className="input-field pl-9" type="password" placeholder="••••••••" required
                    value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
                </div>
              </div>
              <button className="btn-primary w-full mt-2" type="submit" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </button>
              <p className="text-xs text-center text-surface-100 mt-3">
                Demo: <span className="text-brand-500 cursor-pointer" onClick={() => setForm(f => ({ ...f, identifier: 'admin', password: 'admin123' }))}>admin / admin123</span>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-100" />
                  <input className="input-field pl-9" placeholder="John Doe" required
                    value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Username</label>
                <input className="input-field" placeholder="johndoe" required
                  value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} />
              </div>
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Email</label>
                <input className="input-field" type="email" placeholder="john@example.com" required
                  value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
              </div>
              <div>
                <label className="text-xs font-medium text-surface-100 mb-1.5 block">Password</label>
                <input className="input-field" type="password" placeholder="••••••••" required minLength={6}
                  value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
              </div>
              <button className="btn-primary w-full mt-2" type="submit" disabled={loading}>
                {loading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>
          )}
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-3 mt-6">
          {[
            { icon: Eye,    label: 'Eye Tracking' },
            { icon: Zap,    label: 'Real-time AI' },
            { icon: Car,    label: 'Fleet Ready' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="glass p-3 text-center">
              <Icon className="w-5 h-5 text-brand-500 mx-auto mb-1" />
              <span className="text-xs text-surface-100">{label}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
