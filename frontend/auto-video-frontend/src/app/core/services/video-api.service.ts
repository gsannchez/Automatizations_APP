import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from './api-client.service';
import {
  GeneratedVideo,
  GeneratedVideoCreate,
  GeneratedVideoPage,
  GeneratedVideoStatus,
} from '../types/video.types';

@Injectable({ providedIn: 'root' })
export class VideoApiService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  list(page = 1, limit = 20): Observable<GeneratedVideoPage> {
    const params = new HttpParams().set('page', page).set('limit', limit);
    return this.http.get<GeneratedVideoPage>(this.api.url('/videos/'), { params });
  }

  get(id: string): Observable<GeneratedVideo> {
    return this.http.get<GeneratedVideo>(this.api.url(`/videos/${id}`));
  }

  create(data: GeneratedVideoCreate): Observable<GeneratedVideo> {
    return this.http.post<GeneratedVideo>(this.api.url('/videos/'), data);
  }

  getStatus(id: string): Observable<GeneratedVideoStatus> {
    return this.http.get<GeneratedVideoStatus>(this.api.url(`/videos/${id}/status`));
  }

  generate(id: string): Observable<{ message: string; video_id: string }> {
    return this.http.post<{ message: string; video_id: string }>(
      this.api.url(`/videos/${id}/generate`),
      {}
    );
  }

  retry(id: string): Observable<{ message: string; video_id: string }> {
    return this.http.post<{ message: string; video_id: string }>(
      this.api.url(`/videos/${id}/retry`),
      {}
    );
  }

  update(
    id: string,
    body: { status?: string; storage_key?: string; scenes_data?: unknown[] }
  ): Observable<GeneratedVideo> {
    return this.http.patch<GeneratedVideo>(this.api.url(`/videos/${id}`), body);
  }

  getDownloadUrl(id: string): Observable<{ download_url: string; filename?: string }> {
    return this.http.get<{ download_url: string; filename?: string }>(
      this.api.url(`/videos/${id}/download`)
    );
  }

  downloadBlob(url: string): Observable<Blob> {
    const fullUrl = url.startsWith('http') ? url : `${this.api.baseUrl}${url}`;
    return this.http.get(fullUrl, { responseType: 'blob' });
  }
}
