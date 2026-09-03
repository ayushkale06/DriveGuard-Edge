'use client'
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import Cookies from 'js-cookie'
import api from '@/lib/api'

interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: string
  avatar_url?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (identifier: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = Cookies.get('access_token') || localStorage.getItem('access_token')
    if (savedToken) {
      setToken(savedToken)
      api.get('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => { Cookies.remove('access_token'); localStorage.removeItem('access_token') })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (identifier: string, password: string) => {
    const form = new URLSearchParams()
    form.append('username', identifier)
    form.append('password', password)
    const res = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    const { access_token, user: u } = res.data
    Cookies.set('access_token', access_token, { expires: 1 })
    localStorage.setItem('access_token', access_token)
    setToken(access_token)
    setUser(u)
  }

  const logout = () => {
    Cookies.remove('access_token')
    localStorage.removeItem('access_token')
    setUser(null)
    setToken(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
