'use client'
import { useRef, useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, CameraOff, AlertTriangle, Shield, Eye, Activity, Zap } from 'lucide-react'
import { getRiskColor, getRiskLabel, getStateColor } from '@/lib/utils'
import { WS_BASE } from '@/lib/api'
import toast from 'react-hot-toast'

interface AIData {
  driver: string
  faces: number
  ear: number
  mar: number
  blinks: number
  yawns: number
  eyes: string
  head_pose: string
  pitch: number
  yaw: number
  yawning: boolean
  phone: string
  seatbelt: string
  emotion: string
  risk_score: number
  risk_status: string
  fps: number
}

const defaultData: AIData = {
  driver: 'NO FACE', faces: 0, ear: 0, mar: 0, blinks: 0, yawns: 0,
  eyes: '--', head_pose: '--', pitch: 0, yaw: 0, yawning: false,
  phone: 'NO', seatbelt: 'YES', emotion: 'N/A', risk_score: 100, risk_status: 'SAFE', fps: 0
}

const Metric = ({ label, value, color }: { label: string; value: string | number; color?: string }) => (
  <div className="glass p-3 text-center">
    <div className="text-xs text-surface-100 mb-1">{label}</div>
    <div className="text-lg font-bold" style={{ color: color || '#f0f6fc' }}>{value}</div>
  </div>
)

export default function MonitoringPage() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const [isRunning, setIsRunning] = useState(false)
  const [data, setData] = useState<AIData>(defaultData)
  const [annotatedFrame, setAnnotatedFrame] = useState<string | null>(null)
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected')

  const riskHistory = useRef<number[]>([])

  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || video.videoWidth === 0) return null
    canvas.width = 640
    canvas.height = 480
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(video, 0, 0, 640, 480)
    const b64 = canvas.toDataURL('image/jpeg', 0.7)
    return b64.split(',')[1]
  }, [])

  const startMonitoring = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      // Connect WebSocket
      const wsUrl = `${WS_BASE}/api/v1/ai/ws/stream`
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      setWsStatus('connecting')

      ws.onopen = () => {
        setWsStatus('connected')
        // Send frames at ~10 FPS
        intervalRef.current = setInterval(() => {
          if (ws.readyState !== WebSocket.OPEN) return
          const frame = captureFrame()
          if (frame) ws.send(JSON.stringify({ frame }))
        }, 100)
      }

      ws.onmessage = (evt) => {
        const msg = JSON.parse(evt.data)
        if (msg.frame) setAnnotatedFrame(`data:image/jpeg;base64,${msg.frame}`)
        if (msg.data) {
          setData(msg.data)
          riskHistory.current = [...riskHistory.current.slice(-59), msg.data.risk_score]
          // Alert on critical
          if (msg.data.risk_status === 'CRITICAL') {
            toast.error('🚨 Critical risk detected!', { id: 'critical', duration: 3000 })
          }
        }
      }

      ws.onerror = () => { setWsStatus('disconnected'); toast.error('AI stream error') }
      ws.onclose = () => setWsStatus('disconnected')

      setIsRunning(true)
    } catch (err) {
      toast.error('Camera access denied or not available')
    }
  }, [captureFrame])

  const stopMonitoring = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    if (wsRef.current) wsRef.current.close()
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    if (videoRef.current) videoRef.current.srcObject = null
    setIsRunning(false)
    setAnnotatedFrame(null)
    setData(defaultData)
    setWsStatus('disconnected')
  }, [])

  useEffect(() => () => stopMonitoring(), [stopMonitoring])

  const riskColor = getRiskColor(data.risk_score)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Live Monitoring</h1>
          <p className="text-surface-100 text-sm mt-0.5">Real-time AI driver monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
            wsStatus === 'connected' ? 'text-green-400 border-green-500/30 bg-green-500/10' :
            wsStatus === 'connecting' ? 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10' :
            'text-gray-400 border-gray-600/30 bg-gray-600/10'
          }`}>
            <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-green-400 animate-pulse' : wsStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' : 'bg-gray-400'}`} />
            {wsStatus.toUpperCase()}
          </div>
          {!isRunning ? (
            <button onClick={startMonitoring} className="btn-primary flex items-center gap-2">
              <Camera className="w-4 h-4" /> Start
            </button>
          ) : (
            <button onClick={stopMonitoring}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 transition-colors">
              <CameraOff className="w-4 h-4" /> Stop
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Camera Feed */}
        <div className="xl:col-span-2 space-y-4">
          <div className="glass overflow-hidden relative" style={{ aspectRatio: '4/3' }}>
            {annotatedFrame ? (
              <img src={annotatedFrame} alt="AI Feed" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-surface-100">
                <video ref={videoRef} className={`w-full h-full object-cover ${isRunning ? '' : 'hidden'}`} muted playsInline />
                {!isRunning && (
                  <>
                    <Camera className="w-16 h-16 mb-4 opacity-30" />
                    <p className="text-sm">Click Start to begin monitoring</p>
                  </>
                )}
              </div>
            )}
            <canvas ref={canvasRef} className="hidden" />

            {/* Risk overlay */}
            {isRunning && (
              <div className="absolute top-3 right-3">
                <div className="glass px-3 py-2 text-center" style={{ minWidth: 80 }}>
                  <div className="text-2xl font-bold" style={{ color: riskColor }}>{data.risk_score}%</div>
                  <div className="text-xs font-medium" style={{ color: riskColor }}>{data.risk_status}</div>
                </div>
              </div>
            )}

            {/* State badge */}
            {isRunning && data.driver !== 'NO FACE' && (
              <div className="absolute top-3 left-3">
                <div className="px-3 py-1.5 rounded-full text-xs font-bold border"
                  style={{ color: getStateColor(data.driver), background: `${getStateColor(data.driver)}18`, borderColor: `${getStateColor(data.driver)}40` }}>
                  {data.driver}
                </div>
              </div>
            )}

            {/* Alert banner */}
            <AnimatePresence>
              {isRunning && ['DROWSY', 'PHONE DETECTED', 'CRITICAL'].includes(data.driver) && (
                <motion.div initial={{ y: 60 }} animate={{ y: 0 }} exit={{ y: 60 }}
                  className="absolute bottom-0 left-0 right-0 flex items-center gap-3 px-4 py-3"
                  style={{ background: 'rgba(239,68,68,0.9)' }}>
                  <AlertTriangle className="w-5 h-5 text-white" />
                  <span className="text-white font-bold text-sm">⚠ {data.driver} — Take action immediately!</span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Mini metrics */}
          <div className="grid grid-cols-6 gap-2">
            <Metric label="FPS"    value={data.fps}          color="#00c8ff" />
            <Metric label="Faces"  value={data.faces}        color="#22c55e" />
            <Metric label="EAR"    value={data.ear.toFixed(2)} color={data.ear < 0.21 ? '#ef4444' : '#8b949e'} />
            <Metric label="MAR"    value={data.mar.toFixed(2)} color={data.mar > 0.6  ? '#ef4444' : '#8b949e'} />
            <Metric label="Blinks" value={data.blinks}       color="#7c3aed" />
            <Metric label="Yawns"  value={data.yawns}        color="#f97316" />
          </div>
        </div>

        {/* Status Panel */}
        <div className="space-y-4">
          {/* Driver Status */}
          <div className="glass p-5">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-500" /> Driver Status
            </h3>
            <div className="text-center py-4">
              <div className="text-4xl font-black mb-1" style={{ color: getStateColor(data.driver) }}>
                {data.driver}
              </div>
              <div className="text-sm text-surface-100">Current State</div>
            </div>
            <div className="mt-4 space-y-2">
              {[
                { label: 'Eyes',      value: data.eyes,          ok: data.eyes !== 'CLOSED' },
                { label: 'Head',      value: data.head_pose,     ok: data.head_pose === 'FORWARD' || data.head_pose === '--' },
                { label: 'Phone',     value: data.phone,         ok: data.phone !== 'YES' },
                { label: 'Seatbelt',  value: data.seatbelt,      ok: data.seatbelt !== 'NO' },
                { label: 'Emotion',   value: data.emotion,       ok: true },
              ].map(({ label, value, ok }) => (
                <div key={label} className="flex items-center justify-between text-sm">
                  <span className="text-surface-100">{label}</span>
                  <span className={`font-medium ${ok ? 'text-green-400' : 'text-red-400'}`}>{value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Head Pose */}
          <div className="glass p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Eye className="w-4 h-4 text-brand-500" /> Head Pose
            </h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                { label: 'Direction', value: data.head_pose },
                { label: 'Pitch',     value: `${data.pitch}°` },
                { label: 'Yaw',       value: `${data.yaw}°` },
              ].map(({ label, value }) => (
                <div key={label} className="flex flex-col">
                  <span className="text-xs text-surface-100">{label}</span>
                  <span className="font-semibold text-white">{value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Modules Status */}
          <div className="glass p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-brand-500" /> AI Modules
            </h3>
            <div className="space-y-1.5">
              {[
                'Face Detection', 'Face Mesh', 'Eye Tracking', 'Blink Detection',
                'Drowsiness', 'Head Pose', 'Yawn Detection', 'Phone Detection',
              ].map(mod => (
                <div key={mod} className="flex items-center justify-between text-xs">
                  <span className="text-surface-100">{mod}</span>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                    <span className="text-green-400">Active</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
