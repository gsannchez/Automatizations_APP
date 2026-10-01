export type VideoPlatform = 'TIKTOK' | 'REELS' | 'SHORTS' | string;
export type VideoStatus = string;
export type PipelineState = string;
export type SceneStatus = 'PENDING' | 'AUDIO_GENERATED' | 'READY' | string;

export interface SceneProgressEntry {
  image?: string;
  audio?: string;
}

export interface SceneData {
  scene_id?: string;
  text?: string;
  emotion?: string;
  character?: string;
  image_path?: string;
  audio_path?: string;
  duration?: number;
  status?: SceneStatus;
  image_prompt?: string;
  voiceover_text?: string;
  narration?: string;
  [key: string]: unknown;
}

export interface GeneratedVideo {
  id: string;
  user_id?: string;
  template_id: string;
  title: string;
  platform: VideoPlatform;
  status: VideoStatus;
  pipeline_state?: PipelineState;
  progress: number;
  storage_key?: string | null;
  duration_seconds?: number | null;
  error_message?: string | null;
  error_step?: string | null;
  created_at: string;
  updated_at: string;
  topic?: string | null;
  channel_id?: number | null;
  scenes_data?: SceneData[] | null;
  scene_progress?: Record<string, SceneProgressEntry> | null;
}

export interface GeneratedVideoStatus {
  id: string;
  status: VideoStatus;
  pipeline_state?: PipelineState;
  progress: number;
  error_message?: string | null;
  error_step?: string | null;
  scenes_data?: SceneData[] | null;
  scene_progress?: Record<string, SceneProgressEntry> | null;
}

export interface GeneratedVideoPage {
  items: GeneratedVideo[];
  total: number;
  page: number;
  limit: number;
}

export interface GeneratedVideoCreate {
  template_id: string;
  title: string;
  platform: string;
  topic?: string;
  channel_id?: string;
  style_config?: Record<string, unknown>;
}
