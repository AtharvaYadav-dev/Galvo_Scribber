import React, { useEffect, useState, useCallback } from 'react';
import { 
  Zap, 
  Radio, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Thermometer, 
  Crosshair, 
  Flame, 
  Sparkles 
} from 'lucide-react';
import { TelemetryData, PortInfo } from '../lib/types';
import { hardwareApi, onBridgeReady } from '../lib/pywebview';

interface TopNavProps {
  telemetry: TelemetryData;
  onRefreshPorts?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ telemetry }) => {
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [selectedPort, setSelectedPort] = useState<string>('COM3');
  const [selectedBaud, setSelectedBaud] = useState<number>(115200);
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [isPulsing, setIsPulsing] = useState<boolean>(false);

  const refreshPorts = useCallback(async () => {
    try {
      const list = await hardwareApi.getAvailablePorts();
      setPorts(list);
      if (list.length > 0 && !list.find(p => p.port === selectedPort)) {
        setSelectedPort(list[0].port);
      }
    } catch (e) {
      console.error('Failed to get ports:', e);
    }
  }, [selectedPort]);

  useEffect(() => {
    refreshPorts();
    // Auto-refresh when bridge ready event triggers
    onBridgeReady(() => {
      refreshPorts();
    });
  }, [refreshPorts]);

  const handleConnectToggle = async () => {
    setIsConnecting(true);
    try {
      if (telemetry.connected) {
        await hardwareApi.disconnectDevice();
      } else {
        await hardwareApi.connectDevice(selectedPort, selectedBaud);
      }
    } catch (err) {
      console.error('Connection toggle error:', err);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleEStop = async () => {
    if (telemetry.estop_active) {
      await hardwareApi.resetEstop();
    } else {
      await hardwareApi.emergencyStop();
    }
  };

  // Test Laser Pulse (50ms safety burst)
  const handleTestPulse = async () => {
    if (telemetry.estop_active || isPulsing) return;
    setIsPulsing(true);
    try {
      await hardwareApi.setLaser(true);
      setTimeout(async () => {
        await hardwareApi.setLaser(false);
        setIsPulsing(false);
      }, 60);
    } catch (e) {
      setIsPulsing(false);
    }
  };

  return (
    <header className="h-16 bg-[#0c0d12]/95 border-b border-zinc-800/80 px-4 flex items-center justify-between select-none backdrop-blur-md z-30 shrink-0">
      {/* Brand & System Status */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/10 border border-cyan-500/30">
          <Zap className="w-5 h-5 text-cyan-400" />
          <span className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${telemetry.connected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-zinc-600'} animate-pulse`} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-bold tracking-wider text-white uppercase font-mono">
              GALVO STUDIO <span className="text-cyan-400">PRO</span>
            </h1>
            <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/50">
              GT-MOTION U3
            </span>
            <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/50">
              {telemetry.active_cor_file || '100mm.cor'}
            </span>
            {telemetry.is_mock && (
              <span className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-amber-950/70 text-amber-300 border border-amber-800/50">
                SIMULATION
              </span>
            )}
          </div>
          <p className="text-[11px] text-zinc-400 font-mono flex items-center gap-2">
            <span>MFP-5W-70W Q-SWITCH</span>
            <span className="text-zinc-600">•</span>
            <span>100x100mm FIELD</span>
          </p>
        </div>
      </div>

      {/* Middle Status Telemetry Badges */}
      <div className="hidden lg:flex items-center gap-3 font-mono text-xs">
        {/* DO1 Laser State */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
          telemetry.laser_state 
            ? 'bg-rose-950/60 border-rose-600/80 text-rose-300 shadow-[0_0_12px_rgba(244,63,94,0.4)] animate-pulse' 
            : 'bg-zinc-900/60 border-zinc-800 text-zinc-500'
        }`}>
          <Flame className={`w-4 h-4 ${telemetry.laser_state ? 'text-rose-400' : 'text-zinc-600'}`} />
          <span className="font-semibold">DO1 (LASER):</span>
          <span>{telemetry.laser_state ? 'FIRING' : 'OFF'}</span>
        </div>

        {/* DO2 Red Dot Pointer State */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
          telemetry.reddot_state 
            ? 'bg-red-950/50 border-red-500/70 text-red-300 shadow-[0_0_10px_rgba(239,68,68,0.3)]' 
            : 'bg-zinc-900/60 border-zinc-800 text-zinc-500'
        }`}>
          <span className={`w-2.5 h-2.5 rounded-full ${telemetry.reddot_state ? 'bg-red-500 shadow-[0_0_6px_#ef4444]' : 'bg-zinc-700'}`} />
          <span className="font-semibold">DO2 (POINTER):</span>
          <span>{telemetry.reddot_state ? 'ON' : 'OFF'}</span>
        </div>

        {/* Test Pulse Button */}
        <button
          onClick={handleTestPulse}
          disabled={telemetry.estop_active || isPulsing}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-cyan-300 transition-colors cursor-pointer text-xs font-mono disabled:opacity-40"
          title="Fire 50ms test pulse"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>PULSE 50ms</span>
        </button>

        {/* Coordinates Position */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-zinc-300">
          <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-zinc-400">X:</span>
          <span className="text-cyan-300 font-semibold">{telemetry.cur_x.toFixed(2)}</span>
          <span className="text-zinc-400">Y:</span>
          <span className="text-cyan-300 font-semibold">{telemetry.cur_y.toFixed(2)}</span>
          <span className="text-zinc-500">mm</span>
        </div>

        {/* Temperature */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-zinc-300">
          <Thermometer className="w-3.5 h-3.5 text-emerald-400" />
          <span>{telemetry.temperature.toFixed(1)}°C</span>
        </div>
      </div>

      {/* Right Controls: Serial COM + E-STOP */}
      <div className="flex items-center gap-3">
        {/* Serial Port Selector */}
        <div className="flex items-center gap-1.5 bg-zinc-900/80 border border-zinc-800 rounded-lg p-1">
          <select 
            aria-label="Serial COM Port"
            value={selectedPort} 
            onChange={(e) => setSelectedPort(e.target.value)}
            disabled={telemetry.connected}
            className="bg-transparent text-xs text-zinc-200 font-mono px-2 py-1 outline-none cursor-pointer disabled:text-zinc-500"
          >
            {ports.map((p) => (
              <option key={p.port} value={p.port} className="bg-zinc-900 text-zinc-200">
                {p.port} - {p.desc}
              </option>
            ))}
          </select>

          <select 
            aria-label="Baud Rate"
            value={selectedBaud} 
            onChange={(e) => setSelectedBaud(Number(e.target.value))}
            disabled={telemetry.connected}
            className="bg-transparent text-xs text-zinc-400 font-mono px-1 py-1 outline-none cursor-pointer border-l border-zinc-800 disabled:text-zinc-600"
          >
            <option value={9600} className="bg-zinc-900">9600</option>
            <option value={57600} className="bg-zinc-900">57600</option>
            <option value={115200} className="bg-zinc-900">115200</option>
            <option value={250000} className="bg-zinc-900">250000</option>
          </select>

          <button
            onClick={refreshPorts}
            disabled={telemetry.connected}
            className="p-1 text-zinc-400 hover:text-cyan-400 transition-colors disabled:opacity-30"
            title="Refresh COM Ports"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={handleConnectToggle}
            disabled={isConnecting}
            className={`px-3 py-1 rounded text-xs font-semibold font-mono flex items-center gap-1.5 transition-all ${
              telemetry.connected
                ? 'bg-rose-950/70 hover:bg-rose-900 text-rose-300 border border-rose-800/60'
                : 'bg-cyan-600 hover:bg-cyan-500 text-black shadow-[0_0_12px_rgba(6,182,212,0.3)]'
            }`}
          >
            {telemetry.connected ? (
              <>
                <XCircle className="w-3.5 h-3.5" />
                DISCONNECT
              </>
            ) : (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                CONNECT
              </>
            )}
          </button>
        </div>

        {/* MASSIVE UNMISSABLE EMERGENCY STOP (E-STOP) */}
        <button
          onClick={handleEStop}
          className={`px-4 py-2 rounded-xl font-bold font-mono text-sm tracking-wider flex items-center gap-2 transition-all transform active:scale-95 cursor-pointer shadow-lg ${
            telemetry.estop_active
              ? 'bg-amber-500 hover:bg-amber-400 text-black shadow-[0_0_25px_rgba(245,158,11,0.8)] animate-bounce'
              : 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.7)] border border-red-400/50'
          }`}
          title={telemetry.estop_active ? "Click to Reset E-STOP Latch" : "EMERGENCY STOP - Immediate Laser Cut"}
        >
          <ShieldAlert className="w-5 h-5 text-white animate-pulse" />
          <span>{telemetry.estop_active ? 'RESET E-STOP' : 'EMERGENCY STOP'}</span>
        </button>
      </div>
    </header>
  );
};
