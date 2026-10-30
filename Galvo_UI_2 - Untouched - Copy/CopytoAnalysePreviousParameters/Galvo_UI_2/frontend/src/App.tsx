import React, { useState, useEffect } from 'react';
import { TopNav } from './components/TopNav';
import { LeftPanel } from './components/LeftPanel';
import { CanvasViewer } from './components/CanvasViewer';
import { RightPanel } from './components/RightPanel';
import { BottomConsole } from './components/BottomConsole';
import { TelemetryData, LogEntry, JobParams, MaterialPreset } from './lib/types';
import { hardwareApi } from './lib/pywebview';
import { ShieldAlert } from 'lucide-react';

const initialTelemetry: TelemetryData = {
  connected: false,
  is_mock: true,
  port: null,
  baud: 115200,
  cards_found: 0,
  laser_state: false,
  reddot_state: false,
  power_percent: 25.0,
  analog_val: 63.8,
  analog_voltage: 2.5,
  frequency_khz: 35.0,
  pulse_width_ns: 200,
  mark_speed: 500,
  jump_speed: 1200,
  cur_x: 0.0,
  cur_y: 0.0,
  cur_z: 15.0,
  is_marking: false,
  is_framing: false,
  is_paused: false,
  mark_progress: 0.0,
  estop_active: false,
  temperature: 24.8,
};

const initialJobParams: JobParams = {
  x: 0,
  y: 0,
  width: 40,
  height: 40,
  line_spacing: 0.5,
  edge_offset: 0.2,
  angle: 0,
  loop_count: 1,
  enable_hatch: true,
  shape: 'rect',
  hatch_style: 'scanline',
  text: 'GALVO PRO',
  fontSize: 24,
};

export const App: React.FC = () => {
  const [telemetry, setTelemetry] = useState<TelemetryData>(initialTelemetry);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [jobParams, setJobParams] = useState<JobParams>(initialJobParams);

  // High-Frequency Polling Loop for Hardware Telemetry & Logs with Concurrency Lock
  useEffect(() => {
    let isMounted = true;
    let isPolling = false;

    const poll = async () => {
      if (isPolling) return;
      isPolling = true;
      try {
        const [telemData, logData] = await Promise.all([
          hardwareApi.getTelemetry(),
          hardwareApi.getLogs()
        ]);
        if (isMounted) {
          setTelemetry(telemData);
          setLogs(logData);
        }
      } catch (err) {
        // Bridge initializing
      } finally {
        isPolling = false;
      }
    };

    poll();
    const interval = setInterval(poll, 85);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleClearLogs = async () => {
    await hardwareApi.clearLogs();
    setLogs([]);
  };

  const handleResetEstop = async () => {
    await hardwareApi.resetEstop();
  };

  const handleApplyPreset = (preset: MaterialPreset) => {
    setJobParams((prev) => ({
      ...prev,
      line_spacing: preset.lineSpacing,
      loop_count: preset.loops,
    }));
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#09090b] text-slate-100 font-sans overflow-hidden select-none">
      {/* 1. TOP NAVIGATION & HARDWARE BAR */}
      <TopNav telemetry={telemetry} />

      {/* 2. E-STOP WARNING MODAL BANNER */}
      {telemetry.estop_active && (
        <div className="bg-red-600/90 text-white px-4 py-2 flex items-center justify-between font-mono text-xs z-50 shadow-[0_0_30px_rgba(239,68,68,0.8)] border-b border-red-400">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 animate-bounce" />
            <span className="font-bold tracking-wider">
              CRITICAL: EMERGENCY STOP ACTIVE — ALL LASER POWER & MOTION CUT TO HARD ZERO
            </span>
          </div>
          <button
            onClick={handleResetEstop}
            className="px-3 py-1 bg-white text-red-700 font-bold rounded hover:bg-zinc-100 transition-colors shadow"
          >
            RESET E-STOP LATCH
          </button>
        </div>
      )}

      {/* 3. MAIN WORKSPACE: THREE-COLUMN WORKSTATION LAYOUT */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left: Laser & Beam Parameters + Material Presets + Z Stepper */}
        <LeftPanel 
          telemetry={telemetry} 
          onApplyPreset={handleApplyPreset} 
        />

        {/* Center: 2D Field Visualizer & Interactive Galvo Simulator */}
        <CanvasViewer 
          telemetry={telemetry} 
          jobParams={jobParams} 
          setJobParams={setJobParams} 
        />

        {/* Right: Hatching, Geometry & Motion Planner */}
        <RightPanel 
          telemetry={telemetry} 
          jobParams={jobParams} 
          setJobParams={setJobParams} 
        />
      </div>

      {/* 4. BOTTOM DOCK: REAL-TIME CONSOLE & G-CODE LOGS */}
      <BottomConsole logs={logs} onClearLogs={handleClearLogs} />
    </div>
  );
};

export default App;
