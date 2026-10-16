import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Square, 
  Pause, 
  Eye, 
  Sliders, 
  Layers, 
  RotateCw, 
  Target, 
  Maximize, 
  Circle, 
  Type, 
  Grid3X3, 
  FolderOpen, 
  FileCode, 
  Check, 
  Sparkles 
} from 'lucide-react';
import { TelemetryData, JobParams, VectorFileInfo } from '../lib/types';
import { hardwareApi } from '../lib/pywebview';

interface RightPanelProps {
  telemetry: TelemetryData;
  jobParams: JobParams;
  setJobParams: React.Dispatch<React.SetStateAction<JobParams>>;
}

export const RightPanel: React.FC<RightPanelProps> = ({ 
  telemetry, 
  jobParams, 
  setJobParams 
}) => {
  const [availableFiles, setAvailableFiles] = useState<VectorFileInfo[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string>('');
  const [isLoadingFile, setIsLoadingFile] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Load available sample vector files
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const files = await hardwareApi.getAvailableFiles();
        setAvailableFiles(files);
      } catch (e) {
        console.error('Failed loading file list:', e);
      }
    };
    loadFiles();
  }, []);

  const handleSelectSampleFile = async (name: string) => {
    if (!name) return;
    setSelectedFileName(name);
    setIsLoadingFile(true);
    try {
      const result = await hardwareApi.loadVectorFile(name);
      if (result && result.success) {
        setJobParams((prev) => ({
          ...prev,
          shape: 'file',
          file_name: result.filename,
          vector_paths: result.paths,
          width: result.bounds.width || 40,
          height: result.bounds.height || 40,
          scale_percent: 100,
          x: 0,
          y: 0,
        }));
      }
    } catch (err) {
      console.error('Error loading sample file:', err);
    } finally {
      setIsLoadingFile(false);
    }
  };

  const handleFramingToggle = async () => {
    if (telemetry.is_framing) {
      await hardwareApi.stopFraming();
    } else {
      await hardwareApi.startFraming({
        ...jobParams,
        framing_mode: jobParams.framing_mode || 'bbox',
      });
    }
  };

  const handleStartMarking = async () => {
    if (telemetry.is_marking) {
      await hardwareApi.stopMarking();
    } else {
      await hardwareApi.startMarking(jobParams);
    }
  };

  const handlePauseResume = async () => {
    if (telemetry.is_paused) {
      await hardwareApi.resumeMarking();
    } else {
      await hardwareApi.pauseMarking();
    }
  };

  const updateParam = <K extends keyof JobParams>(key: K, value: JobParams[K]) => {
    setJobParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleFitToField = () => {
    if (jobParams.width > 0 && jobParams.height > 0) {
      const maxDim = Math.max(jobParams.width, jobParams.height);
      const targetDim = 80.0;
      const calcPercent = Math.round((targetDim / maxDim) * 100);
      updateParam('scale_percent', Math.max(10, Math.min(400, calcPercent)));
      updateParam('x', 0);
      updateParam('y', 0);
    }
  };

  const handleLocalFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = async (ev) => {
        const content = ev.target?.result as string;
        if (!content) return;
        const res = await hardwareApi.parseVectorContent(file.name, content);
        if (res && res.success) {
          setJobParams((prev) => ({
            ...prev,
            shape: 'file',
            file_name: res.filename,
            vector_paths: res.paths,
            width: res.bounds.width || 40,
            height: res.bounds.height || 40,
            scale_percent: 100,
            x: 0,
            y: 0,
          }));
        }
      };
      reader.readAsText(file);
      e.target.value = '';
    }
  };

  return (
    <aside className="w-84 bg-[#09090c]/90 border-l border-zinc-800/80 p-4 flex flex-col gap-4 overflow-y-auto select-none shrink-0 font-sans z-20">
      <input
        ref={fileInputRef}
        type="file"
        accept=".svg,.dxf"
        className="hidden"
        onChange={handleLocalFileInput}
      />

      {/* SECTION 1: EXECUTION ACTION CONTROLS */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-3.5 flex flex-col gap-3 shadow-lg">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold tracking-wider text-zinc-400 uppercase font-mono flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-cyan-400" />
            MOTION DISPATCH
          </h2>
          {telemetry.is_marking && (
            <span className="text-[10px] font-mono text-cyan-400 font-bold animate-pulse">
              {telemetry.mark_progress.toFixed(0)}% PROGRESS
            </span>
          )}
        </div>

        {/* Live Progress Bar if marking */}
        {telemetry.is_marking && (
          <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-rose-500 h-full transition-all duration-150"
              style={{ width: `${telemetry.mark_progress}%` }}
            />
          </div>
        )}

        {/* Framing & Marking Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          {/* RUN FRAMING (RED DOT GUIDE) */}
          <button
            onClick={handleFramingToggle}
            disabled={telemetry.estop_active || telemetry.is_marking}
            className={`py-3 px-3 rounded-xl border flex flex-col items-center justify-center gap-1.5 font-mono text-xs font-bold transition-all cursor-pointer ${
              telemetry.is_framing
                ? 'bg-red-950/60 border-red-500 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.4)] animate-pulse'
                : 'bg-zinc-850 hover:bg-zinc-800 border-zinc-700/80 text-zinc-200 hover:text-white'
            } ${telemetry.estop_active || telemetry.is_marking ? 'opacity-40 cursor-not-allowed' : ''}`}
          >
            <Eye className={`w-4 h-4 ${telemetry.is_framing ? 'text-red-400' : 'text-zinc-400'}`} />
            <span>{telemetry.is_framing ? 'STOP FRAMING' : 'RUN FRAMING'}</span>
          </button>

          {/* START MARK / STOP MARK */}
          <button
            onClick={handleStartMarking}
            disabled={telemetry.estop_active}
            className={`py-3 px-3 rounded-xl border flex flex-col items-center justify-center gap-1.5 font-mono text-xs font-bold transition-all cursor-pointer shadow-lg ${
              telemetry.is_marking
                ? 'bg-rose-600 hover:bg-rose-500 text-white border-rose-400 shadow-[0_0_20px_rgba(244,63,94,0.6)] animate-pulse'
                : 'bg-emerald-600 hover:bg-emerald-500 text-black border-emerald-400/60 shadow-[0_0_18px_rgba(16,185,129,0.35)]'
            } ${telemetry.estop_active ? 'opacity-40 cursor-not-allowed' : ''}`}
          >
            {telemetry.is_marking ? (
              <>
                <Square className="w-4 h-4 fill-white" />
                <span>ABORT MARK</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-black" />
                <span>START MARK</span>
              </>
            )}
          </button>
        </div>

        {/* Pause / Resume Controls during Marking */}
        {telemetry.is_marking && (
          <button
            onClick={handlePauseResume}
            className="w-full py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-mono font-semibold text-zinc-300 flex items-center justify-center gap-1.5 transition-colors"
          >
            <Pause className="w-3.5 h-3.5" />
            <span>{telemetry.is_paused ? 'RESUME EXECUTION' : 'PAUSE EXECUTION'}</span>
          </button>
        )}

        {/* Framing Mode Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-zinc-800 text-[11px] font-mono">
          <span className="text-zinc-400">FRAMING MODE:</span>
          <div className="flex bg-zinc-950 p-0.5 rounded border border-zinc-800">
            <button
              onClick={() => updateParam('framing_mode', 'bbox')}
              className={`px-2 py-0.5 rounded text-[10px] ${
                (jobParams.framing_mode || 'bbox') === 'bbox'
                  ? 'bg-cyan-950 text-cyan-300 font-bold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              BOX
            </button>
            <button
              onClick={() => updateParam('framing_mode', 'contour')}
              className={`px-2 py-0.5 rounded text-[10px] ${
                jobParams.framing_mode === 'contour'
                  ? 'bg-cyan-950 text-cyan-300 font-bold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              CONTOUR
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 2: VECTOR SHAPE & CAD FILE SELECTION */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-zinc-300 font-mono uppercase tracking-wider">GEOMETRY TYPE</span>
          {jobParams.shape === 'file' && (
            <span className="text-[10px] font-mono text-cyan-400 font-semibold">CAD IMPORT</span>
          )}
        </div>
        
        <div className="grid grid-cols-6 gap-1 font-mono text-[10px]">
          {[
            { id: 'rect', label: 'Box', icon: Square },
            { id: 'circle', label: 'Circle', icon: Circle },
            { id: 'cross', label: 'Cross', icon: Target },
            { id: 'text', label: 'Text', icon: Type },
            { id: 'grid', label: 'Matrix', icon: Grid3X3 },
            { id: 'file', label: 'File', icon: FileCode },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => updateParam('shape', item.id as any)}
                className={`py-2 rounded flex flex-col items-center justify-center gap-1 border transition-all ${
                  jobParams.shape === item.id
                    ? 'bg-cyan-950/60 border-cyan-500 text-cyan-300 font-bold'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* CAD Vector File Controls */}
        {jobParams.shape === 'file' && (
          <div className="pt-2 flex flex-col gap-2 border-t border-zinc-800/80">
            <div className="flex items-center justify-between">
              <label className="text-zinc-400 text-[10px] font-mono">SAMPLE PARTS</label>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-[10px] font-mono text-cyan-400 hover:underline flex items-center gap-1"
              >
                <FolderOpen className="w-3 h-3" />
                <span>BROWSE...</span>
              </button>
            </div>

            <select
              value={selectedFileName}
              onChange={(e) => handleSelectSampleFile(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 font-mono outline-none focus:border-cyan-500"
            >
              <option value="">-- Choose DXF / SVG file --</option>
              {availableFiles.map((f) => (
                <option key={f.name} value={f.name}>
                  {f.name} ({f.type.toUpperCase()})
                </option>
              ))}
            </select>

            {/* Loaded File Info Card */}
            {jobParams.file_name && (
              <div className="bg-zinc-950/80 border border-zinc-800/80 rounded p-2 text-[10px] font-mono flex flex-col gap-1">
                <div className="flex items-center justify-between text-zinc-300">
                  <span className="font-semibold text-emerald-400">{jobParams.file_name}</span>
                  <span className="text-zinc-500">{jobParams.vector_paths?.length || 0} paths</span>
                </div>
                <div className="text-zinc-400">
                  Natural Size: <span className="text-zinc-200">{jobParams.width.toFixed(1)} x {jobParams.height.toFixed(1)} mm</span>
                </div>
              </div>
            )}

            {/* Scale Percent Slider */}
            <div className="pt-1">
              <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                <span className="text-zinc-400">GEOMETRY SCALE:</span>
                <div className="flex items-center gap-2">
                  <span className="text-cyan-400 font-bold">{jobParams.scale_percent || 100}%</span>
                  <button
                    onClick={handleFitToField}
                    className="text-amber-400 hover:underline"
                    title="Scale to fit comfortably in 80mm area"
                  >
                    FIT (80mm)
                  </button>
                </div>
              </div>
              <input
                type="range"
                min="10"
                max="300"
                step="5"
                value={jobParams.scale_percent || 100}
                onChange={(e) => updateParam('scale_percent', Number(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        )}

        {/* Text Input if Text Shape Selected */}
        {jobParams.shape === 'text' && (
          <div className="pt-1">
            <label className="text-zinc-400 text-[10px] block mb-1 font-mono">ENGRAVING TEXT</label>
            <input 
              type="text"
              value={jobParams.text || 'GALVO PRO'}
              onChange={(e) => updateParam('text', e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-xs text-zinc-100 font-mono focus:border-cyan-500 outline-none"
            />
          </div>
        )}
      </div>

      {/* SECTION 3: DIMENSIONS & OFFSETS */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Maximize className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-zinc-300 font-mono uppercase tracking-wider">DIMENSIONS (MM)</span>
          </div>
          <button 
            onClick={() => setJobParams(p => ({ ...p, x: 0, y: 0 }))}
            className="text-[10px] font-mono text-cyan-400 hover:underline"
          >
            CENTER (0,0)
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div>
            <label className="text-zinc-400 text-[10px] block mb-1">WIDTH</label>
            <input 
              type="number"
              aria-label="Job Width"
              value={jobParams.width}
              onChange={(e) => updateParam('width', Math.max(1, Math.min(100, Number(e.target.value))))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 outline-none focus:border-cyan-500 font-semibold"
            />
          </div>
          <div>
            <label className="text-zinc-400 text-[10px] block mb-1">HEIGHT</label>
            <input 
              type="number"
              aria-label="Job Height"
              value={jobParams.height}
              onChange={(e) => updateParam('height', Math.max(1, Math.min(100, Number(e.target.value))))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 outline-none focus:border-cyan-500 font-semibold"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div>
            <label className="text-zinc-400 text-[10px] block mb-1">OFFSET X</label>
            <input 
              type="number"
              aria-label="Position X Offset"
              value={jobParams.x}
              onChange={(e) => updateParam('x', Math.max(-50, Math.min(50, Number(e.target.value))))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-zinc-400 text-[10px] block mb-1">OFFSET Y</label>
            <input 
              type="number"
              aria-label="Position Y Offset"
              value={jobParams.y}
              onChange={(e) => updateParam('y', Math.max(-50, Math.min(50, Number(e.target.value))))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Quick Size Presets */}
        <div className="flex gap-1.5 pt-1">
          {[
            { label: '20mm', w: 20, h: 20 },
            { label: '40mm', w: 40, h: 40 },
            { label: '60mm', w: 60, h: 60 },
            { label: '80mm', w: 80, h: 80 },
          ].map((item) => (
            <button
              key={item.label}
              onClick={() => {
                updateParam('width', item.w);
                updateParam('height', item.h);
              }}
              className="flex-1 py-1 rounded bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-[10px] font-mono text-zinc-400 hover:text-white transition-colors"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* SECTION 4: INDUSTRIAL HATCHING & FILL */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3.5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold text-zinc-300 font-mono uppercase tracking-wider">HATCHING & FILL</span>
          </div>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input 
              type="checkbox"
              checked={jobParams.enable_hatch}
              onChange={(e) => updateParam('enable_hatch', e.target.checked)}
              className="accent-emerald-400 rounded"
            />
            <span className="text-[10px] font-mono text-zinc-400">ENABLE</span>
          </label>
        </div>

        {jobParams.enable_hatch && (
          <div className="flex flex-col gap-2.5 pt-1">
            {/* Hatch Style */}
            <div className="grid grid-cols-2 gap-1.5 font-mono text-[10px]">
              <button
                onClick={() => updateParam('hatch_style', 'scanline')}
                className={`py-1.5 px-2 rounded border text-center transition-all ${
                  jobParams.hatch_style === 'scanline'
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 font-bold'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                }`}
              >
                SCANLINE (1-WAY)
              </button>
              <button
                onClick={() => updateParam('hatch_style', 'crosshatch')}
                className={`py-1.5 px-2 rounded border text-center transition-all ${
                  jobParams.hatch_style === 'crosshatch'
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 font-bold'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                }`}
              >
                CROSS-HATCH (90°)
              </button>
            </div>

            {/* Line Spacing / Pitch */}
            <div className="flex flex-col gap-1 text-xs font-mono">
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-400">LINE PITCH / SPACING:</span>
                <span className="text-emerald-400 font-bold">{jobParams.line_spacing.toFixed(2)} mm</span>
              </div>
              <input 
                type="range"
                min="0.02"
                max="1.50"
                step="0.01"
                value={jobParams.line_spacing}
                onChange={(e) => updateParam('line_spacing', parseFloat(e.target.value))}
                className="w-full accent-emerald-400 cursor-pointer"
              />
            </div>

            {/* Rotation Angle */}
            <div className="flex flex-col gap-1 text-xs font-mono">
              <div className="flex justify-between text-[10px]">
                <span className="text-zinc-400">ROTATION ANGLE:</span>
                <span className="text-cyan-400 font-bold">{jobParams.angle}°</span>
              </div>
              <input 
                type="range"
                min="0"
                max="180"
                step="5"
                value={jobParams.angle}
                onChange={(e) => updateParam('angle', parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        )}
      </div>

      {/* SECTION 5: MULTI-PASS PASS COUNT */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-3 flex items-center justify-between font-mono text-xs">
        <span className="text-zinc-300 font-bold tracking-wider">LOOP / PASS COUNT:</span>
        <div className="flex items-center gap-1.5">
          {[1, 2, 3, 5, 10].map((count) => (
            <button
              key={count}
              onClick={() => updateParam('loop_count', count)}
              className={`w-7 h-7 rounded border flex items-center justify-center font-bold transition-all ${
                jobParams.loop_count === count
                  ? 'bg-cyan-500 border-cyan-400 text-black shadow-[0_0_8px_rgba(6,182,212,0.5)]'
                  : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-white'
              }`}
            >
              {count}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
