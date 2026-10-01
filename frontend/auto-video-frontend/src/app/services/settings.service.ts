import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '../core/services/api-client.service';

export interface UserSettings {
  gemini_api_key?: string;
  openai_api_key?: string;
  preferred_llm?: string;
  preferred_image_backend?: string;
  preferred_video_backend?: string;
  hybrid_rendering?: boolean;
}

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  getSettings(): Observable<UserSettings> {
    return this.http.get<UserSettings>(this.api.url('/settings'));
  }

  updateSettings(data: Partial<UserSettings>): Observable<UserSettings> {
    return this.http.patch<UserSettings>(this.api.url('/settings'), data);
  }
}
