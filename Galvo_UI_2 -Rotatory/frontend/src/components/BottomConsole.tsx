import React, { useState, useRef, useEffect } from 'react';
import { 
  Terminal, 
  Trash2, 
  ChevronUp, 
  ChevronDown, 
  Send, 
  Download, 
  Play, 
  Square, 
  Zap 
} from 'lucide-react';
import { LogEntry } from '../lib/types';
import { hardwareApi } from '../lib/pywebview';

interface BottomConsoleProps {
  logs: LogEntry[];
  onClearLogs: () => void;
}

const QUICK_GCODES = [
  { label: 'LASER ON', cmd: 'M106 P0 S255', color: 'text-rose-400' },
  { label: 'LASER OFF', cmd: 'M106 P0 S0', color: 'text-zinc-400' },
  { label: 'REDDOT ON', cmd: 'M106 P1 S255', color: 'text-red-400' },
  { label: 'REDDOT OFF', cmd: 'M106 P1 S0', color: 'text-zinc-400' },
  { label: 'CENTER (0,0)', cmd: 'G0 X0 Y0', color: 'text-cyan-400' },
  { label: 'HOME Z', cmd: 'G28 Z', color: 'text-cyan-400' },
  { label: 'POS (M114)', cmd: 'M114', color: 'text-emerald-400' },
  { label: 'ABORT (M410)', cmd: 'M410', color: 'text-amber-400' },
];

export const BottomConsole: React.FC<BottomConsoleProps> = ({ logs, onClearLogs }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [filter, setFilter] = useState<'ALL' | 'GCODE' | 'HARDWARE' | 'SECURITY' | 'ERROR'>('ALL');
  const [cmdInput, setCmdInput] = useState<string>('');
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (autoScroll && isExpanded) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll, isExpanded]);

  const handleSendGcode = async (cmdToSend?: string) => {
    const cmd = (cmdToSend || cmdInput).trim();
    if (!cmd) return;
    await hardwareApi.sendGcode(cmd);
    if (!cmdToSend) {
      setCmdInput('');
    }
  };

  const handleExportLogs = () => {
    const text = logs
      .map((l) => `[${l.timestamp}] [${l.level.toUpperCase()}] [${l.source}]: ${l.message}`)
      .join('\n');
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `galvo_studio_logs_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = logs.filter((log) => {
    if (filter === 'ALL') return true;
    if (filter === 'GCODE') return log.source === 'GCODE' || log.source.startsWith('SERIAL');
    if (filter === 'HARDWARE') return log.source === 'HARDWARE' || log.source === 'MOTION';
    if (filter === 'SECURITY') return log.source === 'SECURITY';
    if (filter === 'ERROR') return log.level === 'error';
    return true;
  });

  const getLogBadge = (log: LogEntry) => {
    switch (log.level) {
      case 'gcode':
        return <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-950/70 text-purple-300 border border-purple-800/40">GCODE</span>;
      case 'error':
        return <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-950/70 text-rose-300 border border-rose-800/40">ERROR</span>;
      case 'warning':
        return <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950/70 text-amber-300 border border-amber-800/40">WARN</span>;
      case 'success':
        return <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/40">OK</span>;
      default:
        return <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950/70 text-cyan-300 border border-cyan-800/40">SYS</span>;
    }
  };

  return (
    <footer className={`bg-[#0a0b10] border-t border-zinc-800/80 flex flex-col transition-all duration-200 select-none shrink-0 z-30 ${
      isExpanded ? 'h-56' : 'h-10'
    }`}>
      {/* Console Header Bar */}
      <div className="h-10 bg-[#0e1017] px-4 flex items-center justify-between border-b border-zinc-800/70 shrink-0 font-mono text-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1.5 text-zinc-300 hover:text-white transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-bold tracking-wider uppercase text-[11px]">HARDWARE & G-CODE CONSOLE</span>
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />}
          </button>

          <span className="text-zinc-600">|</span>

          {/* Filter Pills */}
          <div className="flex items-center gap-1">
            {(['ALL', 'GCODE', 'HARDWARE', 'SECURITY', 'ERROR'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-2 py-0.5 rounded text-[10px] transition-all font-semibold ${
                  filter === tab
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Right Console Actions */}
        <div className="flex items-center gap-2">
          {/* Quick G-Code Macro Pills */}
          <div className="hidden xl:flex items-center gap-1 mr-2 border-r border-zinc-800 pr-2">
            {QUICK_GCODES.map((item) => (
              <button
                key={item.label}
                onClick={() => handleSendGcode(item.cmd)}
                className="px-1.5 py-0.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-[9px] text-zinc-300 hover:text-white transition-colors font-mono"
                title={`Send ${item.cmd}`}
              >
                <span className={item.color}>{item.label}</span>
              </button>
            ))}
          </div>

          <label className="flex items-center gap-1.5 text-[10px] text-zinc-400 cursor-pointer">
            <input 
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="accent-cyan-400 rounded"
            />
            <span>Auto-Scroll</span>
          </label>

          <button
            onClick={handleExportLogs}
            className="p-1 text-zinc-500 hover:text-cyan-400 transition-colors"
            title="Download Logs (.txt)"
          >
            <Download className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onClearLogs}
            className="p-1 text-zinc-500 hover:text-rose-400 transition-colors"
            title="Clear Console Logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Expanded Logs & Input */}
      {isExpanded && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Logs Output Area */}
          <div className="flex-1 overflow-y-auto p-2.5 font-mono text-[11px] space-y-1 bg-[#07080c]">
            {filteredLogs.length === 0 ? (
              <div className="text-zinc-600 italic py-2 text-center text-xs">No logs matching filter</div>
            ) : (
              filteredLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-2.5 hover:bg-zinc-900/40 py-0.5 px-1.5 rounded transition-colors">
                  <span className="text-zinc-600 shrink-0 text-[10px]">{log.timestamp}</span>
                  <div className="shrink-0">{getLogBadge(log)}</div>
                  <span className="text-zinc-400 shrink-0 text-[10px]">[{log.source}]</span>
                  <span className={`break-all ${
                    log.level === 'error' ? 'text-rose-400 font-semibold' :
                    log.level === 'warning' ? 'text-amber-300' :
                    log.level === 'gcode' ? 'text-purple-300 font-bold' :
                    log.level === 'success' ? 'text-emerald-400' : 'text-zinc-300'
                  }`}>
                    {log.message}
                  </span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>

          {/* Quick G-Code Command Input Bar */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSendGcode(); }} 
            className="h-9 bg-[#0b0d14] border-t border-zinc-800/80 px-2 flex items-center gap-2 shrink-0 font-mono text-xs"
          >
            <span className="text-cyan-500 font-bold text-xs select-none pl-1">&gt;</span>
            <input 
              type="text"
              value={cmdInput}
              onChange={(e) => setCmdInput(e.target.value)}
              placeholder="Send G-code or Hardware command (e.g., M106 P0 S255, G1 X10 Y10, G28 Z, M410)..."
              className="flex-1 bg-transparent text-zinc-100 placeholder-zinc-600 outline-none text-xs"
            />
            <button
              type="submit"
              className="px-3 py-1 bg-cyan-600/80 hover:bg-cyan-500 text-black font-bold rounded flex items-center gap-1 transition-all text-[11px] cursor-pointer"
            >
              <Send className="w-3 h-3" />
              <span>SEND</span>
            </button>
          </form>
        </div>
      )}
    </footer>
  );
};
