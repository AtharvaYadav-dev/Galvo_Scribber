import React, { useState, useEffect } from 'react';
import { 
  Flame, 
  Eye, 
  Zap, 
  Activity, 
  Gauge, 
  FastForward, 
  Sliders, 
  Layers, 
  ArrowUp, 
  ArrowDown, 
  Home, 
  Bookmark, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  Check 
} from 'lucide-react';
import { TelemetryData, MaterialPreset } from '../lib/types';
import { hardwareApi } from '../lib/pywebview';

interface LeftPanelProps {
  telemetry: TelemetryData;
  onApplyPreset?: (preset: MaterialPreset) => void;
}

const MATERIAL_PRESETS: MaterialPreset[] = [
  {
    id: 'ss304',
    name: 'Stainless Steel 304',
    material: 'Steel',
    power: 45.0,
    frequency: 35.0,
    markSpeed: 400,
    jumpSpeed: 1200,
    lineSpacing: 0.05,
    loops: 2,
    description: 'High contrast black oxide marking',
  },
  {
    id: 'al6061',
    name: 'Anodized Aluminum',
    material: 'Aluminum',
    power: 70.0,
    frequency: 25.0,
    markSpeed: 300,
    jumpSpeed: 1500,
    lineSpacing: 0.04,
    loops: 3,
    description: 'Deep crisp white contrast engraving',
  },
  {
    id: 'brass',
    name: 'Brass & Copper',
    material: 'Brass',
    power: 60.0,
    frequency: 40.0,
    markSpeed: 500,
    jumpSpeed: 1200,
    lineSpacing: 0.06,
    loops: 2,
    description: 'Precision golden-brown burn finish',
  },
  {
    id: 'silicon',
    name: 'Silicon Wafer / PCB',
    material: 'Silicon',
    power: 18.0,
    frequency: 65.0,
    markSpeed: 850,
    jumpSpeed: 1800,
    lineSpacing: 0.08,
    loops: 1,
    description: 'Ultra-fine thermal trace ablation',
  },
];

export const LeftPanel: React.FC<LeftPanelProps> = ({ telemetry, onApplyPreset }) => {
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');
  const [calibrationFiles, setCalibrationFiles] = useState<string[]>([]);
  const [showDelays, setShowDelays] = useState<boolean>(false);

  // Timing delay local states
  const [onDelay, setOnDelay] = useState<number>(telemetry.laser_on_delay_us || 150);
  const [offDelay, setOffDelay] = useState<number>(telemetry.laser_off_delay_us || 150);
  const [markDelay, setMarkDelay] = useState<number>(telemetry.mark_delay_us || 100);
  const [jumpDelay, setJumpDelay] = useState<number>(telemetry.jump_delay_us || 250);
  const [polyDelay, setPolyDelay] = useState<number>(telemetry.poly_delay_us || 80);

  useEffect(() => {
    const fetchCals = async () => {
      try {
        const list = await hardwareApi.getCalibrationFiles();
        setCalibrationFiles(list);
      } catch (e) {
        console.error('Failed fetching calibration files:', e);
      }
    };
    fetchCals();
  }, []);

  const handleLaserToggle = async () => {
    await hardwareApi.setLaser(!telemetry.laser_state);
  };

  const handleRedDotToggle = async () => {
    await hardwareApi.setRedDot(!telemetry.reddot_state);
  };

  const handlePowerChange = async (val: number) => {
    await hardwareApi.setPower(val);
  };

  const handleFrequencyChange = async (val: number) => {
    await hardwareApi.setFrequency(val);
  };

  const handleMarkSpeedChange = async (val: number) => {
    await hardwareApi.setSpeeds(val, telemetry.jump_speed);
  };

  const handleJumpSpeedChange = async (val: number) => {
    await hardwareApi.setSpeeds(telemetry.mark_speed, val);
  };

  const handleZJog = async (delta: number) => {
    await hardwareApi.moveZ(delta);
  };

  const handleZHome = async () => {
    await hardwareApi.homeZ();
  };

  const handleSelectPreset = async (preset: MaterialPreset) => {
    setSelectedPresetId(preset.id);
    await hardwareApi.setPower(preset.power);
    await hardwareApi.setFrequency(preset.frequency);
    await hardwareApi.setSpeeds(preset.markSpeed, preset.jumpSpeed);
    if (onApplyPreset) {
      onApplyPreset(preset);
    }
  };

  const handleSwitchCalibration = async (filename: string) => {
    if (!filename) return;
    await hardwareApi.setCalibrationFile(filename);
  };

  const handleApplyDelays = async () => {
    await hardwareApi.setLaserDelays(onDelay, offDelay, markDelay, jumpDelay, polyDelay);
  };

  return (
    <aside className="w-80 bg-[#09090c]/90 border-r border-zinc-800/80 p-4 flex flex-col gap-4 overflow-y-auto select-none shrink-0 font-sans z-20">
      {/* SECTION 1: HARDWARE DIGITAL IO BEAM TOGGLES */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-3">
        <h2 className="text-xs font-bold tracking-wider text-zinc-400 uppercase font-mono flex items-center justify-between">
          <span>OPTICAL EMISSION (DO1 / DO2)</span>
          <span className="text-[10px] text-zinc-600">INTERLOCK READY</span>
        </h2>

        <div className="grid grid-cols-2 gap-2">
          {/* Main Laser Toggle (DO1 Pin 0) */}
          <button
            onClick={handleLaserToggle}
            disabled={telemetry.estop_active}
            className={`py-2.5 px-3 rounded-lg border font-mono text-xs font-bold flex flex-col items-center justify-center gap-1 transition-all cursor-pointer ${
              telemetry.laser_state
                ? 'bg-rose-950/80 border-rose-500 text-rose-300 shadow-[0_0_15px_rgba(244,63,94,0.5)] animate-pulse'
                : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200'
            } ${telemetry.estop_active ? 'opacity-40 cursor-not-allowed' : ''}`}
          >
            <Flame className={`w-4 h-4 ${telemetry.laser_state ? 'text-rose-400 fill-rose-500' : 'text-zinc-500'}`} />
            <span>{telemetry.laser_state ? 'LASER EMITTING' : 'FIRE LASER'}</span>
            <span className="text-[9px] font-normal text-zinc-500">DO1 (PIN 0)</span>
          </button>

          {/* Red Dot Pointer Toggle (DO2 Pin 1) */}
          <button
            onClick={handleRedDotToggle}
            disabled={telemetry.estop_active}
            className={`py-2.5 px-3 rounded-lg border font-mono text-xs font-bold flex flex-col items-center justify-center gap-1 transition-all cursor-pointer ${
              telemetry.reddot_state
                ? 'bg-red-950/80 border-red-500 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.5)] animate-pulse'
                : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200'
            } ${telemetry.estop_active ? 'opacity-40 cursor-not-allowed' : ''}`}
          >
            <Eye className={`w-4 h-4 ${telemetry.reddot_state ? 'text-red-400 fill-red-500' : 'text-zinc-500'}`} />
            <span>{telemetry.reddot_state ? 'RED DOT ON' : 'RED GUIDE'}</span>
            <span className="text-[9px] font-normal text-zinc-500">DO2 (PIN 1)</span>
          </button>
        </div>
      </div>

      {/* SECTION 2: ANALOG POWER & FREQUENCY PARAMETERS */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-3">
        <h2 className="text-xs font-bold tracking-wider text-zinc-400 uppercase font-mono flex items-center justify-between">
          <span>BEAM PARAMETERS</span>
          <span className="text-[10px] text-cyan-400 font-mono">0-10V DAC (BIT 2)</span>
        </h2>

        {/* 1. Laser Power Slider (0 - 100%) */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              POWER:
            </span>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-zinc-500">
                {(telemetry.analog_voltage || 0).toFixed(2)}V (DAC: {(telemetry.analog_val || 0).toFixed(0)}/255)
              </span>
              <span className="text-cyan-400 font-bold text-sm">
                {telemetry.power_percent.toFixed(1)}%
              </span>
            </div>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="0.5"
            value={telemetry.power_percent}
            onChange={(e) => handlePowerChange(parseFloat(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
        </div>

        {/* 2. Frequency Q-Switch (20 - 80 kHz) */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              Q-SWITCH FREQ:
            </span>
            <span className="text-emerald-400 font-bold text-sm">
              {telemetry.frequency_khz.toFixed(1)} kHz
            </span>
          </div>
          <input
            type="range"
            min="20"
            max="80"
            step="1"
            value={telemetry.frequency_khz}
            onChange={(e) => handleFrequencyChange(parseFloat(e.target.value))}
            className="w-full accent-emerald-400 cursor-pointer"
          />
        </div>

        {/* 3. Mark Speed (50 - 1800 mm/s) */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5 text-amber-400" />
              MARK SPEED:
            </span>
            <span className="text-amber-400 font-bold text-sm">
              {telemetry.mark_speed.toFixed(0)} mm/s
            </span>
          </div>
          <input
            type="range"
            min="50"
            max="1800"
            step="25"
            value={telemetry.mark_speed}
            onChange={(e) => handleMarkSpeedChange(parseFloat(e.target.value))}
            className="w-full accent-amber-400 cursor-pointer"
          />
        </div>

        {/* 4. Jump Speed (100 - 1870 mm/s) */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <FastForward className="w-3.5 h-3.5 text-purple-400" />
              JUMP SPEED:
            </span>
            <span className="text-purple-400 font-bold text-sm">
              {telemetry.jump_speed.toFixed(0)} mm/s
            </span>
          </div>
          <input
            type="range"
            min="100"
            max="1870"
            step="50"
            value={telemetry.jump_speed}
            onChange={(e) => handleJumpSpeedChange(parseFloat(e.target.value))}
            className="w-full accent-purple-400 cursor-pointer"
          />
        </div>
      </div>

      {/* SECTION 3: LENS CALIBRATION (.COR) SELECTOR */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="font-bold text-zinc-300">LENS CALIBRATION (.COR)</span>
          <span className="text-[10px] text-emerald-400 font-semibold">65x65 MATRIX</span>
        </div>
        <select
          value={telemetry.active_cor_file || 'newest100mm.cor'}
          onChange={(e) => handleSwitchCalibration(e.target.value)}
          className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 font-mono outline-none focus:border-cyan-500"
        >
          {calibrationFiles.map((cor) => (
            <option key={cor} value={cor}>
              {cor}
            </option>
          ))}
        </select>
      </div>

      {/* SECTION 4: LASER TIMING & DELAYS (COLLAPSIBLE) */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3 flex flex-col gap-2">
        <button
          onClick={() => setShowDelays(!showDelays)}
          className="flex items-center justify-between text-xs font-mono font-bold text-zinc-300 hover:text-white"
        >
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>OPTICAL DELAYS (µS)</span>
          </div>
          {showDelays ? <ChevronUp className="w-4 h-4 text-zinc-400" /> : <ChevronDown className="w-4 h-4 text-zinc-400" />}
        </button>

        {showDelays && (
          <div className="pt-2 flex flex-col gap-2 border-t border-zinc-800 text-[11px] font-mono">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-500 text-[10px] block mb-0.5">LASER ON (µS)</label>
                <input
                  type="number"
                  value={onDelay}
                  onChange={(e) => setOnDelay(Number(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1 text-zinc-200 outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-zinc-500 text-[10px] block mb-0.5">LASER OFF (µS)</label>
                <input
                  type="number"
                  value={offDelay}
                  onChange={(e) => setOffDelay(Number(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1 text-zinc-200 outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1.5">
              <div>
                <label className="text-zinc-500 text-[10px] block mb-0.5">MARK (µS)</label>
                <input
                  type="number"
                  value={markDelay}
                  onChange={(e) => setMarkDelay(Number(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-1.5 py-1 text-zinc-200 outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-zinc-500 text-[10px] block mb-0.5">JUMP (µS)</label>
                <input
                  type="number"
                  value={jumpDelay}
                  onChange={(e) => setJumpDelay(Number(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-1.5 py-1 text-zinc-200 outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-zinc-500 text-[10px] block mb-0.5">POLY (µS)</label>
                <input
                  type="number"
                  value={polyDelay}
                  onChange={(e) => setPolyDelay(Number(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-1.5 py-1 text-zinc-200 outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <button
              onClick={handleApplyDelays}
              className="mt-1 w-full py-1 rounded bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800/60 text-cyan-300 font-bold text-center"
            >
              SAVE TIMING PARAMETERS
            </button>
          </div>
        )}
      </div>

      {/* SECTION 5: Z-AXIS FOCUS STEPPER MOTOR CONTROLS */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-2.5">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="font-bold text-zinc-300">Z-AXIS FOCUS STEPPER</span>
          <span className="text-cyan-400 font-bold">{telemetry.cur_z.toFixed(2)} mm</span>
        </div>

        <div className="grid grid-cols-4 gap-1.5 font-mono text-xs">
          <button
            onClick={() => handleZJog(1.0)}
            className="py-1.5 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 flex items-center justify-center gap-0.5"
          >
            <ArrowUp className="w-3.5 h-3.5 text-cyan-400" />
            <span>+1.0</span>
          </button>
          <button
            onClick={() => handleZJog(0.1)}
            className="py-1.5 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 flex items-center justify-center gap-0.5"
          >
            <ArrowUp className="w-3.5 h-3.5 text-cyan-400" />
            <span>+0.1</span>
          </button>
          <button
            onClick={() => handleZJog(-0.1)}
            className="py-1.5 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 flex items-center justify-center gap-0.5"
          >
            <ArrowDown className="w-3.5 h-3.5 text-rose-400" />
            <span>-0.1</span>
          </button>
          <button
            onClick={() => handleZJog(-1.0)}
            className="py-1.5 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 flex items-center justify-center gap-0.5"
          >
            <ArrowDown className="w-3.5 h-3.5 text-rose-400" />
            <span>-1.0</span>
          </button>
        </div>

        <button
          onClick={handleZHome}
          className="w-full py-1.5 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 font-mono text-xs flex items-center justify-center gap-1.5 transition-colors"
        >
          <Home className="w-3.5 h-3.5 text-cyan-400" />
          <span>HOME Z AXIS (G28 Z)</span>
        </button>
      </div>

      {/* SECTION 6: INDUSTRIAL MATERIAL PRESETS */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-2">
        <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-400 font-bold uppercase tracking-wider">
          <Bookmark className="w-3.5 h-3.5 text-amber-400" />
          <span>MATERIAL PRESETS</span>
        </div>

        <div className="flex flex-col gap-1.5">
          {MATERIAL_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => handleSelectPreset(preset)}
              className={`p-2 rounded-lg border text-left transition-all font-mono text-xs cursor-pointer ${
                selectedPresetId === preset.id
                  ? 'bg-cyan-950/40 border-cyan-500 text-cyan-200'
                  : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-zinc-200">
                <span>{preset.name}</span>
                {selectedPresetId === preset.id && <Check className="w-3.5 h-3.5 text-cyan-400" />}
              </div>
              <div className="text-[10px] text-zinc-500 mt-0.5 flex items-center gap-2">
                <span>{preset.power}% Pwr</span>
                <span>•</span>
                <span>{preset.frequency}kHz</span>
                <span>•</span>
                <span>{preset.markSpeed}mm/s</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
