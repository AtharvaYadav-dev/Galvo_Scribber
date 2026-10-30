import React, { useRef, useEffect, useState, useCallback } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Crosshair, 
  Grid, 
  Volume2, 
  VolumeX, 
  UploadCloud, 
  FolderOpen, 
  FileCode, 
  Sparkles 
} from 'lucide-react';
import { TelemetryData, JobParams } from '../lib/types';
import { hardwareApi } from '../lib/pywebview';

interface CanvasViewerProps {
  telemetry: TelemetryData;
  jobParams: JobParams;
  setJobParams?: React.Dispatch<React.SetStateAction<JobParams>>;
}

export const CanvasViewer: React.FC<CanvasViewerProps> = ({ 
  telemetry, 
  jobParams, 
  setJobParams 
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  
  // Viewport transformation: scale (pixels per mm), translation in canvas space
  const [scale, setScale] = useState<number>(4.8);
  const [offset, setOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const [isDraggingJob, setIsDraggingJob] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [cursorMm, setCursorMm] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  // Industrial Acoustic Web Audio Feedback
  const playTone = useCallback((freq: number, duration: number) => {
    if (!audioEnabled) return;
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {
      // AudioContext not available
    }
  }, [audioEnabled]);

  // Audio trigger on laser active transition
  const prevLaserState = useRef(telemetry.laser_state);
  useEffect(() => {
    if (telemetry.laser_state && !prevLaserState.current) {
      playTone(880, 0.15); // High beep on laser start
    } else if (!telemetry.laser_state && prevLaserState.current) {
      playTone(440, 0.12); // Low beep on laser stop
    }
    prevLaserState.current = telemetry.laser_state;
  }, [telemetry.laser_state, playTone]);

  // Convert mouse pixel coordinates to Galvo mm coordinates (-50 to +50 mm)
  const pixelToMm = useCallback((px: number, py: number, width: number, height: number) => {
    const cx = width / 2 + offset.x;
    const cy = height / 2 + offset.y;
    const mmX = (px - cx) / scale;
    const mmY = -(py - cy) / scale;
    return { x: mmX, y: mmY };
  }, [offset, scale]);

  // Convert Galvo mm coordinates to Canvas pixel coordinates
  const mmToPixel = useCallback((mmX: number, mmY: number, width: number, height: number) => {
    const cx = width / 2 + offset.x;
    const cy = height / 2 + offset.y;
    const px = cx + mmX * scale;
    const py = cy - mmY * scale;
    return { x: px, y: py };
  }, [offset, scale]);

  // Mouse Wheel for Zoom
  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    setScale((prev) => Math.max(1.5, Math.min(35.0, prev * zoomFactor)));
  };

  // Check if click hits inside Job bounds
  const isInsideJob = (mm: { x: number; y: number }) => {
    const halfW = (jobParams.width * (jobParams.scale_percent ? jobParams.scale_percent / 100 : 1)) / 2;
    const halfH = (jobParams.height * (jobParams.scale_percent ? jobParams.scale_percent / 100 : 1)) / 2;
    return (
      mm.x >= jobParams.x - halfW &&
      mm.x <= jobParams.x + halfW &&
      mm.y >= jobParams.y - halfH &&
      mm.y <= jobParams.y + halfH
    );
  };

  // Mouse Handlers for Dragging & Panning
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const mm = pixelToMm(mouseX, mouseY, canvas.width, canvas.height);

    if (e.button === 0) { // Left click
      if (setJobParams && isInsideJob(mm) && !e.shiftKey) {
        setIsDraggingJob(true);
        setDragStart({ x: mm.x - jobParams.x, y: mm.y - jobParams.y });
      } else {
        setIsPanning(true);
        setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
      }
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const mm = pixelToMm(mouseX, mouseY, canvas.width, canvas.height);
      setCursorMm({ x: Math.max(-50, Math.min(50, mm.x)), y: Math.max(-50, Math.min(50, mm.y)) });

      if (isDraggingJob && setJobParams) {
        setJobParams((prev) => ({
          ...prev,
          x: Math.max(-50, Math.min(50, Math.round((mm.x - dragStart.x) * 10) / 10)),
          y: Math.max(-50, Math.min(50, Math.round((mm.y - dragStart.y) * 10) / 10)),
        }));
      } else if (isPanning) {
        setOffset({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        });
      }
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setIsDraggingJob(false);
  };

  // Double click to jog Galvo mirror directly
  const handleDoubleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const mm = pixelToMm(mouseX, mouseY, canvas.width, canvas.height);
      hardwareApi.moveToXY(mm.x, mm.y);
    }
  };

  const resetView = () => {
    setScale(4.8);
    setOffset({ x: 0, y: 0 });
  };

  // Drag and Drop File Handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      await loadDroppedFile(file);
    }
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await loadDroppedFile(file);
      e.target.value = '';
    }
  };

  const loadDroppedFile = async (file: File) => {
    const filename = file.name;
    const isSvg = filename.toLowerCase().endsWith('.svg');
    const isDxf = filename.toLowerCase().endsWith('.dxf');

    if (!isSvg && !isDxf) {
      alert('Please upload a valid .svg or .dxf CAD file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = async (event) => {
      const content = event.target?.result as string;
      if (!content) return;
      const result = await hardwareApi.parseVectorContent(filename, content);
      if (result && result.success && setJobParams) {
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
    };
    reader.readAsText(file);
  };

  // Main Canvas Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    
    if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
      canvas.width = width * dpr;
      canvas.height = height * dpr;
    }
    
    ctx.resetTransform();
    ctx.scale(dpr, dpr);

    // 1. Dark Workstation Background
    ctx.fillStyle = '#08090d';
    ctx.fillRect(0, 0, width, height);

    // 2. Galvo 100x100mm Field Box (-50mm to +50mm)
    const fieldTopLeft = mmToPixel(-50, 50, width, height);
    const fieldBottomRight = mmToPixel(50, -50, width, height);
    const fieldW = fieldBottomRight.x - fieldTopLeft.x;
    const fieldH = fieldBottomRight.y - fieldTopLeft.y;

    // Bed background
    ctx.fillStyle = '#0d0f17';
    ctx.fillRect(fieldTopLeft.x, fieldTopLeft.y, fieldW, fieldH);

    // Border
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(fieldTopLeft.x, fieldTopLeft.y, fieldW, fieldH);

    // Corner Accents
    const corner = 14;
    ctx.strokeStyle = '#22d3ee';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(fieldTopLeft.x, fieldTopLeft.y + corner);
    ctx.lineTo(fieldTopLeft.x, fieldTopLeft.y);
    ctx.lineTo(fieldTopLeft.x + corner, fieldTopLeft.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(fieldBottomRight.x - corner, fieldTopLeft.y);
    ctx.lineTo(fieldBottomRight.x, fieldTopLeft.y);
    ctx.lineTo(fieldBottomRight.x, fieldTopLeft.y + corner);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(fieldBottomRight.x, fieldBottomRight.y - corner);
    ctx.lineTo(fieldBottomRight.x, fieldBottomRight.y);
    ctx.lineTo(fieldBottomRight.x - corner, fieldBottomRight.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(fieldTopLeft.x + corner, fieldBottomRight.y);
    ctx.lineTo(fieldTopLeft.x, fieldBottomRight.y);
    ctx.lineTo(fieldTopLeft.x, fieldBottomRight.y - corner);
    ctx.stroke();

    // 3. Millimeter Grid & Coordinate Markings
    if (showGrid) {
      ctx.lineWidth = 0.5;
      for (let mm = -50; mm <= 50; mm += 10) {
        const p1 = mmToPixel(mm, 50, width, height);
        const p2 = mmToPixel(mm, -50, width, height);
        ctx.strokeStyle = mm === 0 ? 'rgba(6, 182, 212, 0.5)' : 'rgba(255, 255, 255, 0.08)';
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();

        const p3 = mmToPixel(-50, mm, width, height);
        const p4 = mmToPixel(50, mm, width, height);
        ctx.strokeStyle = mm === 0 ? 'rgba(6, 182, 212, 0.5)' : 'rgba(255, 255, 255, 0.08)';
        ctx.beginPath();
        ctx.moveTo(p3.x, p3.y);
        ctx.lineTo(p4.x, p4.y);
        ctx.stroke();

        if (scale >= 3) {
          ctx.fillStyle = mm === 0 ? '#06b6d4' : '#71717a';
          ctx.font = '9px "JetBrains Mono", monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'top';
          const originP = mmToPixel(mm, 0, width, height);
          ctx.fillText(`${mm}`, originP.x, originP.y + 4);
        }
      }
    }

    // 4. Center Crosshair (0,0)
    const origin = mmToPixel(0, 0, width, height);
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.8)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(origin.x - 16, origin.y);
    ctx.lineTo(origin.x + 16, origin.y);
    ctx.moveTo(origin.x, origin.y - 16);
    ctx.lineTo(origin.x, origin.y + 16);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(origin.x, origin.y, 4, 0, Math.PI * 2);
    ctx.stroke();

    // 5. Engraving Vector Geometry & Toolpaths
    const scaleMul = jobParams.scale_percent ? jobParams.scale_percent / 100 : 1;
    const effectiveW = jobParams.width * scaleMul;
    const effectiveH = jobParams.height * scaleMul;
    const halfW = effectiveW / 2;
    const halfH = effectiveH / 2;
    const jobCenter = mmToPixel(jobParams.x, jobParams.y, width, height);
    const jobMin = mmToPixel(jobParams.x - halfW, jobParams.y + halfH, width, height);
    const jobMax = mmToPixel(jobParams.x + halfW, jobParams.y - halfH, width, height);
    const jobW = jobMax.x - jobMin.x;
    const jobH = jobMax.y - jobMin.y;

    ctx.save();
    // Rotate canvas around job center if angle specified
    if (jobParams.angle) {
      ctx.translate(jobCenter.x, jobCenter.y);
      ctx.rotate((-jobParams.angle * Math.PI) / 180);
      ctx.translate(-jobCenter.x, -jobCenter.y);
    }

    // A. Render Loaded Vector File Paths (DXF / SVG)
    if (jobParams.shape === 'file' && jobParams.vector_paths && jobParams.vector_paths.length > 0) {
      ctx.strokeStyle = '#06b6d4'; // Cyan neon vector lines
      ctx.lineWidth = 1.4;
      ctx.shadowColor = 'rgba(6, 182, 212, 0.4)';
      ctx.shadowBlur = 4;

      for (const path of jobParams.vector_paths) {
        if (path.length < 2) continue;
        ctx.beginPath();
        const startPt = mmToPixel(jobParams.x + path[0][0] * scaleMul, jobParams.y + path[0][1] * scaleMul, width, height);
        ctx.moveTo(startPt.x, startPt.y);
        for (let i = 1; i < path.length; i++) {
          const pt = mmToPixel(jobParams.x + path[i][0] * scaleMul, jobParams.y + path[i][1] * scaleMul, width, height);
          ctx.lineTo(pt.x, pt.y);
        }
        ctx.stroke();
      }
      ctx.shadowBlur = 0;

      // Subtle dashed bounding box around file
      ctx.strokeStyle = 'rgba(245, 158, 11, 0.5)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.strokeRect(jobMin.x, jobMin.y, jobW, jobH);
      ctx.setLineDash([]);
    } else {
      // B. Procedural Shapes (Box, Circle, Cross, Text, Matrix)
      ctx.strokeStyle = '#f59e0b'; // Amber outline
      ctx.lineWidth = 1.8;

      if (jobParams.shape === 'circle') {
        const radius = Math.min(jobW, jobH) / 2;
        ctx.beginPath();
        ctx.arc(jobCenter.x, jobCenter.y, radius, 0, Math.PI * 2);
        ctx.stroke();
      } else if (jobParams.shape === 'cross') {
        ctx.beginPath();
        ctx.moveTo(jobMin.x, jobCenter.y);
        ctx.lineTo(jobMax.x, jobCenter.y);
        ctx.moveTo(jobCenter.x, jobMin.y);
        ctx.lineTo(jobCenter.x, jobMax.y);
        ctx.stroke();
        ctx.strokeRect(jobMin.x, jobMin.y, jobW, jobH);
      } else if (jobParams.shape === 'text') {
        const text = jobParams.text || 'GALVO PRO';
        ctx.font = `bold ${Math.max(16, jobH * 0.6)}px "JetBrains Mono", monospace`;
        ctx.fillStyle = 'rgba(245, 158, 11, 0.85)';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, jobCenter.x, jobCenter.y);
        ctx.strokeRect(jobMin.x, jobMin.y, jobW, jobH);
      } else if (jobParams.shape === 'grid') {
        // 3x3 Calibration Matrix Array
        const cols = 3;
        const rows = 3;
        const cellW = jobW / cols;
        const cellH = jobH / rows;
        for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
            ctx.strokeRect(jobMin.x + c * cellW + 2, jobMin.y + r * cellH + 2, cellW - 4, cellH - 4);
          }
        }
      } else {
        // Standard Rect Box
        ctx.strokeRect(jobMin.x, jobMin.y, jobW, jobH);
      }

      // Draw Hatching Toolpaths for Procedural Shapes
      if (jobParams.enable_hatch && jobParams.line_spacing > 0.05 && jobParams.shape !== 'text') {
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.45)';
        ctx.lineWidth = 1;

        const spacingMm = Math.max(0.08, jobParams.line_spacing);
        const startY = jobParams.y - halfH + jobParams.edge_offset;
        const endY = jobParams.y + halfH - jobParams.edge_offset;

        // Scanline Hatching
        let cy = startY;
        while (cy <= endY) {
          const p1 = mmToPixel(jobParams.x - halfW + jobParams.edge_offset, cy, width, height);
          const p2 = mmToPixel(jobParams.x + halfW - jobParams.edge_offset, cy, width, height);
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
          cy += spacingMm;
        }

        // Cross-Hatch (90° perpendicular lines)
        if (jobParams.hatch_style === 'crosshatch') {
          let cx = jobParams.x - halfW + jobParams.edge_offset;
          const endX = jobParams.x + halfW - jobParams.edge_offset;
          while (cx <= endX) {
            const p1 = mmToPixel(cx, jobParams.y - halfH + jobParams.edge_offset, width, height);
            const p2 = mmToPixel(cx, jobParams.y + halfH - jobParams.edge_offset, width, height);
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
            cx += spacingMm;
          }
        }
      }
    }

    ctx.restore();

    // 6. Live Marking Progress Highlight
    if (telemetry.is_marking && telemetry.mark_progress > 0) {
      const progressH = jobH * (telemetry.mark_progress / 100);
      ctx.fillStyle = 'rgba(6, 182, 212, 0.18)';
      ctx.fillRect(jobMin.x, jobMin.y + jobH - progressH, jobW, progressH);
    }

    // 7. Live Galvo Mirror Pointer & Beam Emission
    const galvoPos = mmToPixel(telemetry.cur_x, telemetry.cur_y, width, height);

    // Laser Spark & Burn Core when DO1 is EMITTING
    if (telemetry.laser_state) {
      const gradient = ctx.createRadialGradient(galvoPos.x, galvoPos.y, 2, galvoPos.x, galvoPos.y, 26);
      gradient.addColorStop(0, 'rgba(244, 63, 94, 1.0)');
      gradient.addColorStop(0.3, 'rgba(244, 63, 94, 0.7)');
      gradient.addColorStop(1, 'rgba(244, 63, 94, 0)');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(galvoPos.x, galvoPos.y, 26, 0, Math.PI * 2);
      ctx.fill();

      // White-hot plasma core
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(galvoPos.x, galvoPos.y, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Red Dot Pointer Flare
    if (telemetry.reddot_state || telemetry.is_framing) {
      const redGrad = ctx.createRadialGradient(galvoPos.x, galvoPos.y, 1, galvoPos.x, galvoPos.y, 16);
      redGrad.addColorStop(0, 'rgba(239, 68, 68, 0.95)');
      redGrad.addColorStop(0.5, 'rgba(239, 68, 68, 0.4)');
      redGrad.addColorStop(1, 'rgba(239, 68, 68, 0)');
      ctx.fillStyle = redGrad;
      ctx.beginPath();
      ctx.arc(galvoPos.x, galvoPos.y, 16, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#ff2222';
      ctx.beginPath();
      ctx.arc(galvoPos.x, galvoPos.y, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Mirror Crosshair
    ctx.strokeStyle = telemetry.laser_state ? '#f43f5e' : (telemetry.reddot_state ? '#ef4444' : '#06b6d4');
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(galvoPos.x - 12, galvoPos.y);
    ctx.lineTo(galvoPos.x + 12, galvoPos.y);
    ctx.moveTo(galvoPos.x, galvoPos.y - 12);
    ctx.lineTo(galvoPos.x, galvoPos.y + 12);
    ctx.stroke();

  }, [scale, offset, telemetry, jobParams, showGrid, mmToPixel]);

  return (
    <div 
      className={`relative flex-1 h-full w-full bg-[#08090d] overflow-hidden flex flex-col select-none ${
        isDragOver ? 'ring-4 ring-cyan-500/80' : ''
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".svg,.dxf"
        className="hidden"
        onChange={handleFileInputChange}
      />

      {/* Top Floating Viewport Info Bar */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
        <div className="bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-lg px-3 py-1.5 flex items-center gap-3 text-xs font-mono shadow-lg">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
            <span>CURSOR:</span>
            <span className="text-zinc-200 font-bold">{cursorMm.x.toFixed(2)}, {cursorMm.y.toFixed(2)} mm</span>
          </div>
          <div className="h-3 w-px bg-zinc-800" />
          <div className="text-zinc-400">
            <span>FIELD:</span> <span className="text-cyan-400 font-semibold">100 x 100 mm</span>
          </div>
          {jobParams.shape === 'file' && jobParams.file_name && (
            <>
              <div className="h-3 w-px bg-zinc-800" />
              <div className="flex items-center gap-1 text-emerald-400 font-semibold">
                <FileCode className="w-3.5 h-3.5" />
                <span>{jobParams.file_name}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Top Right Floating Toolbar */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-lg p-1 text-zinc-300 shadow-lg font-mono">
        <button
          onClick={() => fileInputRef.current?.click()}
          title="Import DXF / SVG File"
          className="p-1.5 hover:bg-zinc-800 rounded text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-xs px-2"
        >
          <FolderOpen className="w-3.5 h-3.5" />
          <span>IMPORT</span>
        </button>
        <div className="h-4 w-px bg-zinc-800" />
        <button
          onClick={() => setScale((s) => Math.min(35.0, s * 1.2))}
          title="Zoom In"
          className="p-1.5 hover:bg-zinc-800 rounded hover:text-white"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setScale((s) => Math.max(1.5, s * 0.83))}
          title="Zoom Out"
          className="p-1.5 hover:bg-zinc-800 rounded hover:text-white"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={resetView}
          title="Reset Zoom & Pan (Center View)"
          className="p-1.5 hover:bg-zinc-800 rounded hover:text-white"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <div className="h-4 w-px bg-zinc-800" />
        <button
          onClick={() => setShowGrid(!showGrid)}
          title="Toggle Millimeter Grid"
          className={`p-1.5 rounded ${showGrid ? 'bg-cyan-950/60 text-cyan-400' : 'hover:bg-zinc-800 text-zinc-500'}`}
        >
          <Grid className="w-4 h-4" />
        </button>
        <button
          onClick={() => setAudioEnabled(!audioEnabled)}
          title="Toggle Acoustic Beeper Audio"
          className={`p-1.5 rounded ${audioEnabled ? 'bg-amber-950/60 text-amber-400' : 'hover:bg-zinc-800 text-zinc-500'}`}
        >
          {audioEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>
      </div>

      {/* Drag & Drop Visual Overlay Indicator */}
      {isDragOver && (
        <div className="absolute inset-0 z-40 bg-cyan-950/70 backdrop-blur-sm flex flex-col items-center justify-center border-4 border-dashed border-cyan-400 pointer-events-none">
          <UploadCloud className="w-16 h-16 text-cyan-400 animate-bounce mb-3" />
          <h3 className="text-lg font-bold font-mono text-white tracking-wider">DROP CAD FILE HERE</h3>
          <p className="text-xs font-mono text-cyan-200">Supports .SVG and .DXF vector files for laser scribing</p>
        </div>
      )}

      {/* Main Interactive HTML5 Canvas */}
      <canvas
        ref={canvasRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onDoubleClick={handleDoubleClick}
        className="w-full h-full cursor-crosshair block"
      />

      {/* Bottom Floating Canvas Status Bar */}
      <div className="absolute bottom-3 left-3 z-10 flex items-center gap-2">
        <div className="bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-lg px-3 py-1 flex items-center gap-4 text-[11px] font-mono text-zinc-400 shadow-md">
          <span>ZOOM: <span className="text-zinc-200 font-bold">{(scale / 4.8).toFixed(1)}x</span></span>
          <span className="text-zinc-600">•</span>
          <span>DRAG: <span className="text-zinc-200 font-semibold">L-Click Shape / Pan Canvas</span></span>
          <span className="text-zinc-600">•</span>
          <span>DOUBLE CLICK: <span className="text-cyan-400 font-semibold">Jog Mirrors</span></span>
        </div>
      </div>
    </div>
  );
};
