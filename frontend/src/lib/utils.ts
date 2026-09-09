import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

export function getRiskColor(score: number): string {
  if (score >= 85) return '#22c55e'
  if (score >= 65) return '#eab308'
  if (score >= 40) return '#f97316'
  if (score >= 20) return '#ef4444'
  return '#dc2626'
}

export function getRiskLabel(score: number): string {
  if (score >= 85) return 'SAFE'
  if (score >= 65) return 'LOW RISK'
  if (score >= 40) return 'WARNING'
  if (score >= 20) return 'HIGH RISK'
  return 'CRITICAL'
}

export function getStateColor(state: string): string {
  switch (state) {
    case 'SAFE':           return '#22c55e'
    case 'DROWSY':         return '#ef4444'
    case 'PHONE DETECTED': return '#ef4444'
    case 'DISTRACTED':     return '#f97316'
    case 'YAWNING':        return '#eab308'
    case 'NO SEATBELT':    return '#ef4444'
    case 'NO FACE':        return '#6b7280'
    default:               return '#6b7280'
  }
}
