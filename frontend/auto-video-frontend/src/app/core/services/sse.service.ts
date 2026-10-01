import { Injectable, NgZone, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../../environments/environment';
import { OrchestrationEvent } from '../types/system.types';
import { LogStore } from '../stores/log.store';

@Injectable({ providedIn: 'root' })
export class SseService {
  private readonly zone = inject(NgZone);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly logStore = inject(LogStore);
  private source: EventSource | null = null;
  private readonly events$ = new Subject<OrchestrationEvent>();

  readonly stream$ = this.events$.asObservable();

  connectOrchestration(): void {
    if (!isPlatformBrowser(this.platformId) || this.source) return;

    this.source = new EventSource(environment.sseOrchestrationUrl);

    this.source.onmessage = (ev) => {
      this.zone.run(() => {
        const payload: OrchestrationEvent = {
          event: 'message',
          id: ev.lastEventId || crypto.randomUUID(),
          data: ev.data,
        };
        this.events$.next(payload);
        this.logStore.push({
          category: 'workers',
          level: 'info',
          message: ev.data,
          source: 'orchestration-sse',
        });
      });
    };

    this.source.addEventListener('error', () => {
      this.logStore.push({
        category: 'system',
        level: 'warn',
        message: 'Orchestration SSE disconnected; will retry on reconnect',
        source: 'sse',
      });
    });

    // Named events from backend
    const handler = (eventName: string) => (ev: Event) => {
      const msg = ev as MessageEvent;
      this.zone.run(() => {
        this.events$.next({
          event: eventName,
          id: msg.lastEventId || crypto.randomUUID(),
          data: String(msg.data),
        });
      });
    };

    ['agent_update', 'pipeline_update', 'recovery', 'campaign'].forEach((name) => {
      this.source?.addEventListener(name, handler(name));
    });
  }

  disconnect(): void {
    this.source?.close();
    this.source = null;
  }

  createObservable<T>(url: string, mapFn: (data: string) => T): Observable<T> {
    return new Observable((subscriber) => {
      if (!isPlatformBrowser(this.platformId)) {
        subscriber.complete();
        return;
      }
      const es = new EventSource(url);
      es.onmessage = (ev) => this.zone.run(() => subscriber.next(mapFn(ev.data)));
      es.onerror = (err) => this.zone.run(() => subscriber.error(err));
      return () => es.close();
    });
  }
}
