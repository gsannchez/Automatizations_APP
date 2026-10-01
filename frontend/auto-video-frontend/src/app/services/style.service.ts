import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '../core/services/api-client.service';

export interface StylePreset {
  style_id: string;
  name: string;
  prompt_modifier?: string;
  transitions?: string;
  camera_motion?: string;
}

@Injectable({ providedIn: 'root' })
export class StyleService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  listStyles(): Observable<StylePreset[]> {
    return this.http.get<StylePreset[]>(this.api.url('/styles'));
  }

  /** @deprecated use listStyles */
  getStyles(): Observable<StylePreset[]> {
    return this.listStyles();
  }
}
