import { Injectable, inject, signal, computed, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval, forkJoin, of, catchError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { VideoApiService } from '../services/video-api.service';
import { GeneratedVideo, GeneratedVideoStatus } from '../types/video.types';
import { TERMINAL_STATUSES } from '../constants/pipeline.constants';
import { NotificationStore } from './notification.store';

@Injectable({ providedIn: 'root' })
export class VideoStore {
  private readonly api = inject(VideoApiService);
  private readonly notifications = inject(NotificationStore);
  private readonly destroyRef = inject(DestroyRef);

  readonly videos = signal<GeneratedVideo[]>([]);
  readonly total = signal(0);
  readonly page = signal(1);
  readonly limit = signal(20);
  readonly activeVideo = signal<GeneratedVideo | null>(null);
  readonly loading = signal(false);

  readonly activeScenes = computed(() => this.activeVideo()?.scenes_data ?? []);
  readonly totalAudioDuration = computed(() =>
    this.activeScenes().reduce((sum, s) => sum + (s.duration ?? 0), 0)
  );

  readonly processingIds = computed(() =>
    this.videos()
      .filter((v) => !TERMINAL_STATUSES.includes(v.status as (typeof TERMINAL_STATUSES)[number]))
      .map((v) => v.id)
  );

  loadList(page = this.page(), limit = this.limit()): void {
    this.loading.set(true);
    this.api.list(page, limit).subscribe({
      next: (res) => {
        this.videos.set(res.items);
        this.total.set(res.total);
        this.page.set(res.page);
        this.limit.set(res.limit);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  loadVideo(id: string): void {
    this.api.get(id).subscribe({
      next: (v) => this.activeVideo.set(v),
      error: () => this.notifications.error('No se pudo cargar el proyecto'),
    });
  }

  startRealtimePolling(): void {
    interval(environment.statusPollMs)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.pollActiveStatuses());
  }

  pollActiveStatuses(): void {
    const ids = this.processingIds();
    const activeId = this.activeVideo()?.id;
    const allIds = [...new Set([...ids, ...(activeId ? [activeId] : [])])];
    if (!allIds.length) return;

    const requests = allIds.map((id) =>
      this.api.getStatus(id).pipe(catchError(() => of(null)))
    );

    forkJoin(requests).subscribe((updates) => {
      updates.forEach((u) => {
        if (!u) return;
        this.applyStatusUpdate(u);
      });
    });
  }

  private applyStatusUpdate(status: GeneratedVideoStatus): void {
    this.videos.update((list) =>
      list.map((v) => (v.id === status.id ? this.mergeStatus(v, status) : v))
    );
    const active = this.activeVideo();
    if (active?.id === status.id) {
      this.activeVideo.set(this.mergeStatus(active, status));
    }
  }

  private mergeStatus(
    video: GeneratedVideo,
    status: GeneratedVideoStatus
  ): GeneratedVideo {
    return {
      ...video,
      status: status.status,
      pipeline_state: status.pipeline_state ?? video.pipeline_state,
      progress: status.progress,
      error_message: status.error_message ?? video.error_message,
      error_step: status.error_step ?? video.error_step,
      scenes_data: status.scenes_data ?? video.scenes_data,
      scene_progress: status.scene_progress ?? video.scene_progress,
    };
  }
}
