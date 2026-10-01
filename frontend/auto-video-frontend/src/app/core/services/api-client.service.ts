import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiClientService {
  readonly baseUrl = environment.apiBaseUrl;
  readonly apiV1 = environment.apiV1;
  readonly mediaBase = environment.mediaBaseUrl;

  url(path: string): string {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${this.apiV1}${normalized}`;
  }

  mediaUrl(storageKey: string | null | undefined): string | null {
    if (!storageKey) return null;
    if (storageKey.startsWith('http')) return storageKey;
    const key = storageKey.startsWith('/') ? storageKey.slice(1) : storageKey;
    return `${this.mediaBase}/${key}`;
  }
}
