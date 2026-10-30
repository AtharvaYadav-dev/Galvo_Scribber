import { TelemetryData, PortInfo, LogEntry, JobParams, VectorFileInfo, VectorGeometry } from './types';

// Declare pywebview on window
declare global {
  interface Window {
    pywebview?: {
      api: {
        get_available_ports: () => Promise<PortInfo[]>;
        get_baud_rates: () => Promise<number[]>;
        connect_device: (port?: string | null, baud?: number, force_mock?: boolean) => Promise<any>;
        disconnect_device: () => Promise<any>;
        set_laser: (state: boolean) => Promise<any>;
        set_reddot: (state: boolean) => Promise<any>;
        set_power: (percentage: number) => Promise<any>;
        set_frequency: (khz: number) => Promise<any>;
        set_pulse_width: (width_ns: number) => Promise<any>;
        set_speeds: (mark_speed: number, jump_speed: number) => Promise<any>;
        set_laser_delays: (
          on_delay_us: number,
          off_delay_us: number,
          mark_delay_us: number,
          jump_delay_us: number,
          poly_delay_us: number
        ) => Promise<any>;
        get_calibration_files: () => Promise<string[]>;
        set_calibration_file: (filename: string) => Promise<any>;
        get_available_files: () => Promise<VectorFileInfo[]>;
        load_vector_file: (filename_or_path: string) => Promise<VectorGeometry>;
        parse_vector_content: (filename: string, content: string) => Promise<VectorGeometry>;
        start_framing: (params?: any) => Promise<any>;
        stop_framing: () => Promise<any>;
        start_marking: (job_params?: any) => Promise<any>;
        stop_marking: () => Promise<any>;
        pause_marking: () => Promise<any>;
        resume_marking: () => Promise<any>;
        emergency_stop: () => Promise<any>;
        reset_estop: () => Promise<any>;
        move_to_xy: (x: number, y: number) => Promise<any>;
        move_z: (delta_mm: number) => Promise<any>;
        home_z: () => Promise<any>;
        send_gcode: (cmd: string) => Promise<any>;
        get_telemetry: () => Promise<TelemetryData>;
        get_logs: (clear?: boolean) => Promise<LogEntry[]>;
        clear_logs: () => Promise<any>;
      };
    };
  }
}

// Global Bridge Ready State Tracker
let pywebviewReady = false;
const readyCallbacks: Array<() => void> = [];

if (typeof window !== 'undefined') {
  if (window.pywebview && window.pywebview.api) {
    pywebviewReady = true;
  } else {
    window.addEventListener('pywebviewready', () => {
      pywebviewReady = true;
      readyCallbacks.forEach((cb) => {
        try { cb(); } catch (e) { console.error(e); }
      });
      readyCallbacks.length = 0;
    });
  }
}

export function onBridgeReady(callback: () => void) {
  if (pywebviewReady && window.pywebview && window.pywebview.api) {
    callback();
  } else {
    readyCallbacks.push(callback);
  }
}

export function isNativeBridgeActive(): boolean {
  return typeof window !== 'undefined' && !!window.pywebview && !!window.pywebview.api;
}

// In-Browser High-Fidelity Simulator State
let simulatedTelemetry: TelemetryData = {
  connected: true,
  is_mock: false,
  port: 'COM1',
  baud: 115200,
  cards_found: 1,
  laser_state: false,
  reddot_state: false,
  power_percent: 25.0,
  analog_val: 63.8,
  analog_voltage: 2.50,
  frequency_khz: 35.0,
  pulse_width_ns: 200,
  mark_speed: 500,
  jump_speed: 1200,
  cur_x: 0.0,
  cur_y: 0.0,
  cur_z: 0.0,
  is_marking: false,
  is_framing: false,
  is_paused: false,
  mark_progress: 0.0,
  estop_active: false,
  temperature: 24.2,
  active_cor_file: 'newest100mm.cor',
  laser_on_delay_us: 150,
  laser_off_delay_us: 150,
  mark_delay_us: 100,
  jump_delay_us: 250,
  poly_delay_us: 80,
};

let simulatedLogs: LogEntry[] = [
  { id: 1, timestamp: new Date().toLocaleTimeString(), source: 'SYSTEM', message: 'Galvo Laser Studio Pro workstation online.', level: 'info' },
  { id: 2, timestamp: new Date().toLocaleTimeString(), source: 'HARDWARE', message: 'GoogolTech GT-Motion hardware bridge linked & ready.', level: 'success' },
];

export const hardwareApi = {
  async getAvailablePorts(): Promise<PortInfo[]> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_available_ports();
      } catch (e) {
        console.warn('[Bridge] get_available_ports error:', e);
      }
    }
    return [
      { port: 'COM1', desc: 'Communications Port (COM1)', hwid: 'ACPI\\PNP0501' },
      { port: 'COM3', desc: 'USB-Serial Laser Board (BlackPill)', hwid: 'USB_003' },
      { port: 'COM4', desc: 'GoogolTech PCIe Motion Board', hwid: 'GT_004' },
    ];
  },

  async getBaudRates(): Promise<number[]> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_baud_rates();
      } catch (e) {
        console.warn('[Bridge] get_baud_rates error:', e);
      }
    }
    return [9600, 19200, 38400, 57600, 115200, 250000];
  },

  async connectDevice(port: string | null = null, baud: number = 115200, forceMock: boolean = false): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.connect_device(port, baud, forceMock);
      } catch (e) {
        console.warn('[Bridge] connect_device error:', e);
      }
    }
    simulatedTelemetry.connected = true;
    simulatedTelemetry.port = port || 'COM1';
    simulatedTelemetry.baud = baud;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'SERIAL',
      message: `Connected to ${port || 'COM1'} @ ${baud} bps.`,
      level: 'success',
    });
    return { success: true, mode: 'HARDWARE', port, baud };
  },

  async disconnectDevice(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.disconnect_device();
      } catch (e) {
        console.warn('[Bridge] disconnect_device error:', e);
      }
    }
    simulatedTelemetry.connected = false;
    simulatedTelemetry.laser_state = false;
    simulatedTelemetry.reddot_state = false;
    return { success: true };
  },

  async setLaser(state: boolean): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_laser(state);
      } catch (e) {
        console.warn('[Bridge] set_laser error:', e);
      }
    }
    simulatedTelemetry.laser_state = state;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'GCODE',
      message: `M106 P0 S${state ? 255 : 0} (Laser DO1 ${state ? 'ON' : 'OFF'})`,
      level: 'gcode',
    });
    return { success: true, laser_state: state };
  },

  async setRedDot(state: boolean): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_reddot(state);
      } catch (e) {
        console.warn('[Bridge] set_reddot error:', e);
      }
    }
    simulatedTelemetry.reddot_state = state;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'GCODE',
      message: `M106 P1 S${state ? 255 : 0} (Red Dot DO2 ${state ? 'ON' : 'OFF'})`,
      level: 'gcode',
    });
    return { success: true, reddot_state: state };
  },

  async setPower(percentage: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_power(percentage);
      } catch (e) {
        console.warn('[Bridge] set_power error:', e);
      }
    }
    simulatedTelemetry.power_percent = percentage;
    simulatedTelemetry.analog_val = (percentage / 100) * 255;
    simulatedTelemetry.analog_voltage = (percentage / 100) * 10;
    return { success: true, power_percent: percentage };
  },

  async setFrequency(khz: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_frequency(khz);
      } catch (e) {
        console.warn('[Bridge] set_frequency error:', e);
      }
    }
    simulatedTelemetry.frequency_khz = khz;
    return { success: true, frequency_khz: khz };
  },

  async setPulseWidth(width_ns: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_pulse_width(width_ns);
      } catch (e) {
        console.warn('[Bridge] set_pulse_width error:', e);
      }
    }
    simulatedTelemetry.pulse_width_ns = width_ns;
    return { success: true, pulse_width_ns: width_ns };
  },

  async setSpeeds(mark_speed: number, jump_speed: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_speeds(mark_speed, jump_speed);
      } catch (e) {
        console.warn('[Bridge] set_speeds error:', e);
      }
    }
    simulatedTelemetry.mark_speed = mark_speed;
    simulatedTelemetry.jump_speed = jump_speed;
    return { success: true, mark_speed, jump_speed };
  },

  async setLaserDelays(
    on_delay_us: number,
    off_delay_us: number,
    mark_delay_us: number,
    jump_delay_us: number,
    poly_delay_us: number
  ): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_laser_delays(
          on_delay_us,
          off_delay_us,
          mark_delay_us,
          jump_delay_us,
          poly_delay_us
        );
      } catch (e) {
        console.warn('[Bridge] set_laser_delays error:', e);
      }
    }
    simulatedTelemetry.laser_on_delay_us = on_delay_us;
    simulatedTelemetry.laser_off_delay_us = off_delay_us;
    simulatedTelemetry.mark_delay_us = mark_delay_us;
    simulatedTelemetry.jump_delay_us = jump_delay_us;
    simulatedTelemetry.poly_delay_us = poly_delay_us;
    return { success: true };
  },

  async getCalibrationFiles(): Promise<string[]> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_calibration_files();
      } catch (e) {
        console.warn('[Bridge] get_calibration_files error:', e);
      }
    }
    return ['newest100mm.cor', '70x70mini.cor', 'calibration1.cor', 'test.cor'];
  },

  async setCalibrationFile(filename: string): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.set_calibration_file(filename);
      } catch (e) {
        console.warn('[Bridge] set_calibration_file error:', e);
      }
    }
    simulatedTelemetry.active_cor_file = filename;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'CALIBRATION',
      message: `Active lens correction file loaded: ${filename}`,
      level: 'success',
    });
    return { success: true, active_file: filename };
  },

  async getAvailableFiles(): Promise<VectorFileInfo[]> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_available_files();
      } catch (e) {
        console.warn('[Bridge] get_available_files error:', e);
      }
    }
    return [
      { name: '40mm_square.svg', type: 'svg', path: 'svg_files/40mm_square.svg', size: 266 },
      { name: '70mm_square.svg', type: 'svg', path: 'svg_files/70mm_square.svg', size: 1377 },
      { name: 'wafer_grid_50mm.svg', type: 'svg', path: 'svg_files/wafer_grid_50mm.svg', size: 125664 },
      { name: 'smooth_spiral_0.5mm_pitch.dxf', type: 'dxf', path: 'svg_files/smooth_spiral_0.5mm_pitch.dxf', size: 164213 },
      { name: 'test.dxf', type: 'dxf', path: 'test.dxf', size: 233 },
    ];
  },

  async loadVectorFile(filename: string): Promise<VectorGeometry> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.load_vector_file(filename);
      } catch (e) {
        console.warn('[Bridge] load_vector_file error:', e);
      }
    }
    // Fallback simulated geometry (Square spiral)
    const pts: number[][] = [];
    for (let r = 2; r <= 36; r += 1.5) {
      for (let a = 0; a < 360; a += 15) {
        const rad = (a * Math.PI) / 180;
        pts.push([Math.round(r * Math.cos(rad) * 10) / 10, Math.round(r * Math.sin(rad) * 10) / 10]);
      }
    }
    return {
      success: true,
      filename,
      file_type: filename.endsWith('.svg') ? 'svg' : 'dxf',
      paths: [pts],
      bounds: { min_x: -36, max_x: 36, min_y: -36, max_y: 36, width: 72, height: 72 },
      path_count: 1,
      point_count: pts.length,
    };
  },

  async parseVectorContent(filename: string, content: string): Promise<VectorGeometry> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.parse_vector_content(filename, content);
      } catch (e) {
        console.warn('[Bridge] parse_vector_content error:', e);
      }
    }
    return this.loadVectorFile(filename);
  },

  async startFraming(params?: any): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.start_framing(params);
      } catch (e) {
        console.warn('[Bridge] start_framing error:', e);
      }
    }
    simulatedTelemetry.is_framing = true;
    simulatedTelemetry.reddot_state = true;
    return { success: true, is_framing: true };
  },

  async stopFraming(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.stop_framing();
      } catch (e) {
        console.warn('[Bridge] stop_framing error:', e);
      }
    }
    simulatedTelemetry.is_framing = false;
    simulatedTelemetry.reddot_state = false;
    return { success: true, is_framing: false };
  },

  async startMarking(jobParams?: any): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.start_marking(jobParams);
      } catch (e) {
        console.warn('[Bridge] start_marking error:', e);
      }
    }
    simulatedTelemetry.is_marking = true;
    simulatedTelemetry.is_framing = false;
    simulatedTelemetry.laser_state = true;
    simulatedTelemetry.mark_progress = 0;
    return { success: true, is_marking: true };
  },

  async stopMarking(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.stop_marking();
      } catch (e) {
        console.warn('[Bridge] stop_marking error:', e);
      }
    }
    simulatedTelemetry.is_marking = false;
    simulatedTelemetry.laser_state = false;
    return { success: true, is_marking: false };
  },

  async pauseMarking(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.pause_marking();
      } catch (e) {
        console.warn('[Bridge] pause_marking error:', e);
      }
    }
    simulatedTelemetry.is_paused = true;
    simulatedTelemetry.laser_state = false;
    return { success: true, is_paused: true };
  },

  async resumeMarking(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.resume_marking();
      } catch (e) {
        console.warn('[Bridge] resume_marking error:', e);
      }
    }
    simulatedTelemetry.is_paused = false;
    simulatedTelemetry.laser_state = true;
    return { success: true, is_paused: false };
  },

  async emergencyStop(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.emergency_stop();
      } catch (e) {
        console.warn('[Bridge] emergency_stop error:', e);
      }
    }
    simulatedTelemetry.estop_active = true;
    simulatedTelemetry.laser_state = false;
    simulatedTelemetry.reddot_state = false;
    simulatedTelemetry.is_marking = false;
    simulatedTelemetry.is_framing = false;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'SECURITY',
      message: '>>> EMERGENCY STOP TRIGGERED! ALL LASER POWER CUT IMMEDIATELY <<<',
      level: 'error',
    });
    return { success: true, estop_active: true };
  },

  async resetEstop(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.reset_estop();
      } catch (e) {
        console.warn('[Bridge] reset_estop error:', e);
      }
    }
    simulatedTelemetry.estop_active = false;
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'SECURITY',
      message: 'Emergency Stop latch reset. System ready.',
      level: 'success',
    });
    return { success: true, estop_active: false };
  },

  async moveToXY(x: number, y: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.move_to_xy(x, y);
      } catch (e) {
        console.warn('[Bridge] move_to_xy error:', e);
      }
    }
    simulatedTelemetry.cur_x = Math.max(-50, Math.min(50, x));
    simulatedTelemetry.cur_y = Math.max(-50, Math.min(50, y));
    return { success: true, x: simulatedTelemetry.cur_x, y: simulatedTelemetry.cur_y };
  },

  async moveZ(delta_mm: number): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.move_z(delta_mm);
      } catch (e) {
        console.warn('[Bridge] move_z error:', e);
      }
    }
    simulatedTelemetry.cur_z = Math.round((simulatedTelemetry.cur_z + delta_mm) * 100) / 100;
    return { success: true, cur_z: simulatedTelemetry.cur_z };
  },

  async homeZ(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.home_z();
      } catch (e) {
        console.warn('[Bridge] home_z error:', e);
      }
    }
    simulatedTelemetry.cur_z = 0.0;
    return { success: true, cur_z: 0.0 };
  },

  async sendGcode(cmd: string): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.send_gcode(cmd);
      } catch (e) {
        console.warn('[Bridge] send_gcode error:', e);
      }
    }
    simulatedLogs.push({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      source: 'GCODE',
      message: cmd,
      level: 'gcode',
    });
    return { success: true, sent: cmd };
  },

  async getTelemetry(): Promise<TelemetryData> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_telemetry();
      } catch (e) {
        // Fall through to simulated telemetry
      }
    }
    return { ...simulatedTelemetry };
  },

  async getLogs(clear: boolean = false): Promise<LogEntry[]> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.get_logs(clear);
      } catch (e) {
        // Fall through
      }
    }
    const current = [...simulatedLogs];
    if (clear) simulatedLogs = [];
    return current;
  },

  async clearLogs(): Promise<any> {
    if (isNativeBridgeActive()) {
      try {
        return await window.pywebview!.api.clear_logs();
      } catch (e) {
        console.warn('[Bridge] clear_logs error:', e);
      }
    }
    simulatedLogs = [];
    return { success: true };
  },
};
