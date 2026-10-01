import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from './api-client.service';

@Injectable({ providedIn: 'root' })
export class OrchestrationApiService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  getStatus(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(this.api.url('/orchestration/status'));
  }

  getQueueHealth(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(this.api.url('/orchestration/queue-health'));
  }

  getSystemLoad(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(this.api.url('/orchestration/system-load'));
  }

  getAgents(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(this.api.url('/orchestration/agents'));
  }
}
