import { Injectable, inject, signal, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval, switchMap, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SystemApiService } from '../services/system-api.service';
import { OrchestrationApiService } from '../services/orchestration-api.service';
import { PipelineStatusResponse } from '../types/system.types';
import { LogStore } from './log.store';

@Injectable({ providedIn: 'root' })
export class SystemStore {
  private readonly systemApi = inject(SystemApiService);
  private readonly orchApi = inject(OrchestrationApiService);
  private readonly logStore = inject(LogStore);
  private readonly destroyRef = inject(DestroyRef);

  readonly pipelineStatus = signal<PipelineStatusResponse | null>(null);
  readonly queueHealth = signal<Record<string, unknown> | null>(null);
  readonly loading = signal(false);
  readonly lastUpdated = signal<Date | null>(null);
  readonly apiError = signal<string | null>(null);

  startMonitoring(): void {
    this.refresh();

    interval(environment.systemHealthPollMs)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        switchMap(() => this.systemApi.getPipelineStatus().pipe(catchError((err) => of({ error: err }))))
      )
      .subscribe((result) => {
        if ('error' in result && result.error) {
          this.apiError.set('Backend no disponible');
          this.logStore.push({
            category: 'backend',
            level: 'error',
            message: 'No se pudo obtener estado del sistema',
            source: 'system',
          });
          return;
        }
        this.apiError.set(null);
        this.pipelineStatus.set(result as PipelineStatusResponse);
        this.lastUpdated.set(new Date());
      });

    interval(environment.systemHealthPollMs * 2)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        switchMap(() => this.orchApi.getQueueHealth().pipe(catchError(() => of(null))))
      )
      .subscribe((q) => this.queueHealth.set(q));
  }

  refresh(): void {
    this.loading.set(true);
    this.systemApi.getPipelineStatus().subscribe({
      next: (s) => {
        this.pipelineStatus.set(s);
        this.lastUpdated.set(new Date());
        this.apiError.set(null);
        this.loading.set(false);
      },
      error: () => {
        this.apiError.set('Backend no disponible — inicia el API en el puerto 8000');
        this.loading.set(false);
      },
    });
  }
}
