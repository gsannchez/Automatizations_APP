export interface CeleryHealth {
  available: boolean;
  workers?: number;
  error?: string;
}

export interface GpuMetrics {
  usage_percent?: number;
  total_mb?: number;
  used_mb?: number;
  free_mb?: number;
  device_name?: string;
  [key: string]: unknown;
}

export interface PipelineHealth {
  status: 'healthy' | 'degraded' | 'critical' | string;
  quality_tier?: string;
  gpu?: GpuMetrics;
  safe_to_start_new_task?: boolean;
  celery?: CeleryHealth;
}

export interface ComfyUiStatus {
  url?: string;
  reachable?: boolean;
  error?: string;
  [key: string]: unknown;
}

export interface PipelineStatusResponse {
  pipeline: PipelineHealth;
  gpu: GpuMetrics;
  comfyui: ComfyUiStatus;
}

export interface OrchestrationEvent {
  event: string;
  id: string;
  data: string;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  category: 'backend' | 'workers' | 'comfyui' | 'ffmpeg' | 'audio' | 'timeline' | 'system';
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  source?: string;
}
