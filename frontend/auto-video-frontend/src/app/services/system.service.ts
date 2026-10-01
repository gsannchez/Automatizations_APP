import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { SystemApiService } from '../core/services/system-api.service';
import { PipelineHealth } from '../core/types/system.types';

@Injectable({ providedIn: 'root' })
export class SystemService {
  private readonly api = inject(SystemApiService);

  getPipelineHealth(): Observable<PipelineHealth> {
    return this.api.getHealth();
  }
}
