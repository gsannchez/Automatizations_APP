import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface VideoSnippet {
  id: string;
  title: string;
  status: string;
  progress: number;
  created_at: string;
}

export interface VideoPage {
  items: VideoSnippet[];
  total: number;
  page: number;
  limit: number;
}

export interface VideoStatusUpdate {
  id: string;
  status: string;
  progress: number;
}

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private readonly API_URL = '/api/v1/videos';

  constructor(private http: HttpClient) {}

  listVideos(page: number = 1, limit: number = 20): Observable<VideoPage> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    
    return this.http.get<VideoPage>(`${this.API_URL}/`, { params });
  }

  createVideo(data: any): Observable<VideoSnippet> {
    return this.http.post<VideoSnippet>(`${this.API_URL}/`, data);
  }

  getVideoStatus(videoId: string): Observable<VideoStatusUpdate> {
    return this.http.get<VideoStatusUpdate>(`${this.API_URL}/${videoId}/status`);
  }

  getDownloadUrl(videoId: string): Observable<{ download_url: string }> {
    return this.http.get<{ download_url: string }>(`${this.API_URL}/${videoId}/download`);
  }

  generateVideo(videoId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/${videoId}/generate`, {});
  }
}
