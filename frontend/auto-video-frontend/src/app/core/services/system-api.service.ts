import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from './api-client.service';
import {
  ComfyUiStatus,
  GpuMetrics,
  PipelineHealth,
  PipelineStatusResponse,
} from '../types/system.types';

@Injectable({ providedIn: 'root' })
export class SystemApiService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  getHealth(): Observable<PipelineHealth> {
    return this.http.get<PipelineHealth>(`${this.api.apiV1}/system/health`);
  }

  getGpu(): Observable<GpuMetrics> {
    return this.http.get<GpuMetrics>(`${this.api.apiV1}/system/gpu`);
  }

  getComfyUi(): Observable<ComfyUiStatus> {
    return this.http.get<ComfyUiStatus>(`${this.api.apiV1}/system/comfyui`);
  }

  getPipelineStatus(): Observable<PipelineStatusResponse> {
    return this.http.get<PipelineStatusResponse>(`${this.api.apiV1}/system/pipeline-status`);
  }
}
