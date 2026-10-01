export interface UserProfile {
  id: string;
  email: string;
  plan: string;
  minutes_used?: number;
  created_at?: string;
}

export interface AuthStats {
  total_videos: number;
  active_channels: number;
  total_templates: number;
  processing_videos: number;
  plan: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
