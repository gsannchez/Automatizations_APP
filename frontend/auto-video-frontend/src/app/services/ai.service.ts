import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '../core/services/api-client.service';

export interface AIScriptRequest {
  topic: string;
  platform?: string;
  num_scenes?: number;
}

export interface AIScene {
  text?: string;
  voiceover_text?: string;
  image_prompt?: string;
  duration?: number;
}

export interface AIScriptResponse {
  scenes: AIScene[];
}

export interface AITextEnhanceRequest {
  title: string;
  topic: string;
}

export interface AITextEnhanceResponse {
  title: string;
  topic: string;
}

@Injectable({ providedIn: 'root' })
export class AiService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  generateScript(body: AIScriptRequest): Observable<AIScriptResponse> {
    return this.http.post<AIScriptResponse>(this.api.url('/ai/generate-script'), body);
  }

  enhanceText(body: AITextEnhanceRequest): Observable<AITextEnhanceResponse> {
    return this.http.post<AITextEnhanceResponse>(this.api.url('/ai/enhance-text'), body);
  }
}
