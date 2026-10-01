import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '../core/services/api-client.service';

export interface Template {
  id: string;
  name: string;
  platform: string;
  description?: string;
  is_active?: boolean;
  sort_order?: number;
  style_config?: Record<string, unknown>;
  recommended_duration?: number;
  structure_json?: string;
}

export interface TemplateCreatePayload {
  name: string;
  platform: string;
  description?: string;
  style_config?: Record<string, unknown>;
  recommended_duration?: number;
  structure_json?: string;
}

@Injectable({ providedIn: 'root' })
export class TemplateService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  getTemplates(): Observable<Template[]> {
    return this.http.get<Template[]>(this.api.url('/templates'));
  }

  createTemplate(template: TemplateCreatePayload): Observable<Template> {
    return this.http.post<Template>(this.api.url('/templates'), template);
  }

  deleteTemplate(id: string): Observable<{ deleted: boolean }> {
    return this.http.delete<{ deleted: boolean }>(this.api.url(`/templates/${id}`));
  }
}
