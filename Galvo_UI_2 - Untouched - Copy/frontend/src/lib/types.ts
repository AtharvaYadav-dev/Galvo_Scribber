export interface TelemetryData {
  connected: boolean;
  is_mock: boolean;
  port: string | null;
  baud: number;
  cards_found: number;
  laser_state: boolean;
  reddot_state: boolean;
  power_percent: number;
  analog_val: number;
  analog_voltage: number;
  frequency_khz: number;
  pulse_width_ns: number;
  mark_speed: number;
  jump_speed: number;
  cur_x: number;
  cur_y: number;
  cur_z: number;
  is_marking: boolean;
  is_framing: boolean;
  is_paused: boolean;
  mark_progress: number;
  estop_active: boolean;
  temperature: number;
  active_cor_file?: string;
  laser_on_delay_us?: number;
  laser_off_delay_us?: number;
  mark_delay_us?: number;
  jump_delay_us?: number;
  poly_delay_us?: number;
}

export interface PortInfo {
  port: string;
  desc: string;
  hwid: string;
}

export interface LogEntry {
  id: number;
  timestamp: string;
  source: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error' | 'gcode';
}

export interface VectorFileInfo {
  name: string;
  type: 'svg' | 'dxf';
  path: string;
  size: number;
}

export interface VectorGeometry {
  success: boolean;
  error?: string;
  filename: string;
  file_type: 'svg' | 'dxf';
  paths: number[][][]; // Array of paths, each path is array of [x, y] points in mm
  bounds: {
    min_x: number;
    max_x: number;
    min_y: number;
    max_y: number;
    width: number;
    height: number;
  };
  path_count: number;
  point_count: number;
}

export interface JobParams {
  x: number;
  y: number;
  width: number;
  height: number;
  line_spacing: number;
  edge_offset: number;
  angle: number;
  loop_count: number;
  enable_hatch: boolean;
  shape: 'rect' | 'circle' | 'cross' | 'grid' | 'text' | 'file';
  hatch_style: 'scanline' | 'crosshatch' | 'spiral';
  text?: string;
  fontSize?: number;
  vector_paths?: number[][][];
  file_name?: string;
  scale_percent?: number;
  framing_mode?: 'bbox' | 'contour';
}

export interface MaterialPreset {
  id: string;
  name: string;
  material: string;
  power: number;
  frequency: number;
  markSpeed: number;
  jumpSpeed: number;
  lineSpacing: number;
  loops: number;
  description: string;
}
