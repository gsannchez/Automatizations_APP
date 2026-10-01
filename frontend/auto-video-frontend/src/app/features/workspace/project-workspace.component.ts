import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { VideoStore } from '../../core/stores/video.store';
import { VideoApiService } from '../../core/services/video-api.service';
import { ApiClientService } from '../../core/services/api-client.service';
import { NotificationStore } from '../../core/stores/notification.store';
import { AvProgressComponent } from '../../shared/components/ui/av-progress.component';
import { AvButtonComponent } from '../../shared/components/ui/av-button.component';
import { AvCardComponent } from '../../shared/components/ui/av-card.component';
import { TimelineTrackComponent } from './components/timeline-track.component';
import { SceneManagerComponent } from './components/scene-manager.component';
import { PipelineVisualizerComponent } from './components/pipeline-visualizer.component';
import { SceneData } from '../../core/types/video.types';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-project-workspace',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    AvProgressComponent,
    AvButtonComponent,
    AvCardComponent,
    TimelineTrackComponent,
    SceneManagerComponent,
    PipelineVisualizerComponent,
  ],
  template: `
    @if (loadError()) {
      <div class="workspace-error av-surface">
        <p>{{ loadError() }}</p>
        <a routerLink="/videos">Volver a proyectos</a>
      </div>
    } @else if (video(); as v) {
      <div class="workspace">
        <header class="workspace__header">
          <div>
            <a routerLink="/videos" class="back">← Proyectos</a>
            <h1>{{ v.title }}</h1>
            <p class="meta">{{ v.platform }} · {{ v.pipeline_state || v.status }} · {{ v.progress }}%</p>
          </div>
          <div class="workspace__actions">
            <av-progress [value]="v.progress" label="Progreso global" />
            @if (v.status === 'DONE') {
              <av-button (click)="download()">Descargar</av-button>
            }
            @if (v.status === 'FAILED' || (v.status !== 'DONE' && v.progress < 100)) {
              <av-button variant="secondary" (click)="retry()">Reintentar generación</av-button>
            }
          </div>
        </header>

        <div class="workspace__grid">
          <aside class="workspace__left">
            <av-card title="Pipeline" subtitle="Estado real del backend">
              <av-pipeline-visualizer
                [pipelineState]="v.pipeline_state ?? v.status"
                [progress]="v.progress"
                [errorMessage]="v.error_message ?? null"
              />
            </av-card>
            <av-scene-manager
              [scenes]="scenes()"
              [sceneProgress]="v.scene_progress ?? null"
              [selectedIndex]="selectedScene()"
              (select)="selectedScene.set($event)"
              (regenerate)="retry()"
              (saveScenes)="persistScenes($event)"
            />
          </aside>

          <main class="workspace__center">
            <av-card title="Preview" subtitle="Vídeo y escena seleccionada">
              <div class="preview">
                @if (previewVideoUrl()) {
                  <video class="preview__video" [src]="previewVideoUrl()" controls playsinline></video>
                } @else if (previewImageUrl(); as img) {
                  <img class="preview__video" [src]="img" alt="Escena" />
                } @else {
                  <div class="preview__placeholder">
                    <span>{{ statusMessage() }}</span>
                    <av-progress [value]="v.progress" [indeterminate]="v.progress < 5 && v.status !== 'FAILED'" />
                  </div>
                }
                @if (selectedSceneData(); as scene) {
                  <div class="preview__scene-detail">
                    <h4>Escena {{ selectedScene()! + 1 }}</h4>
                    <p>{{ scene.text || scene.voiceover_text || '—' }}</p>
                    @if (scene.image_prompt) {
                      <p class="prompt"><strong>Prompt:</strong> {{ scene.image_prompt }}</p>
                    }
                  </div>
                }
              </div>
            </av-card>
          </main>

          <aside class="workspace__right">
            <av-card title="Propiedades">
              <dl class="props">
                <dt>ID</dt>
                <dd class="mono">{{ v.id }}</dd>
                <dt>Estado</dt>
                <dd>{{ v.status }}</dd>
                <dt>Pipeline</dt>
                <dd>{{ v.pipeline_state || '—' }}</dd>
                <dt>Duración audio</dt>
                <dd>{{ totalAudio() | number: '1.1-1' }}s</dd>
                <dt>Escenas</dt>
                <dd>{{ scenes().length }}</dd>
                @if (v.error_message) {
                  <dt>Error</dt>
                  <dd class="error">{{ v.error_message }}</dd>
                }
                @if (v.error_step) {
                  <dt>Paso</dt>
                  <dd class="error">{{ v.error_step }}</dd>
                }
              </dl>
            </av-card>
          </aside>
        </div>

        <footer class="workspace__timeline">
          <av-timeline-track
            [scenes]="scenes()"
            [selectedIndex]="selectedScene()"
            [sceneProgress]="v.scene_progress ?? null"
            (sceneSelect)="selectedScene.set($event)"
          />
        </footer>
      </div>
    } @else {
      <p class="loading">Cargando proyecto…</p>
    }
  `,
  styles: [
    `
      .workspace {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        animation: fadeUp 0.3s ease;
      }
      .workspace-error {
        padding: 2rem;
        border-radius: var(--radius-lg);
        text-align: center;
      }
      .loading {
        color: var(--text-muted);
        padding: 2rem;
      }
      .workspace__header {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
      }
      .workspace__header h1 {
        margin: 0.25rem 0;
      }
      .back {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      .meta {
        font-size: 0.8125rem;
        color: var(--text-muted);
      }
      .workspace__actions {
        min-width: 200px;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      }
      .workspace__grid {
        display: grid;
        grid-template-columns: 280px 1fr 240px;
        gap: 1rem;
      }
      @media (max-width: 1100px) {
        .workspace__grid {
          grid-template-columns: 1fr;
        }
      }
      .workspace__left,
      .workspace__right {
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      .preview__video {
        width: 100%;
        max-height: 360px;
        border-radius: var(--radius-md);
        background: #000;
      }
      .preview__placeholder {
        padding: 2rem;
        text-align: center;
        background: var(--bg-hover);
        border-radius: var(--radius-md);
        color: var(--text-muted);
      }
      .preview__scene-detail {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
        font-size: 0.8125rem;
      }
      .prompt {
        color: var(--text-secondary);
        margin-top: 0.5rem;
      }
      .props {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 0.35rem 0.75rem;
        font-size: 0.8125rem;
      }
      .props dt {
        color: var(--text-muted);
      }
      .props .mono {
        font-size: 0.6875rem;
        word-break: break-all;
      }
      .props .error {
        color: var(--danger);
      }
    `,
  ],
})
export class ProjectWorkspaceComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly store = inject(VideoStore);
  private readonly api = inject(VideoApiService);
  private readonly media = inject(ApiClientService);
  private readonly notifications = inject(NotificationStore);

  readonly video = this.store.activeVideo;
  readonly selectedScene = signal<number | null>(0);
  readonly loadError = signal<string | null>(null);
  readonly previewVideoUrl = signal<string | null>(null);

  readonly scenes = computed(() => this.video()?.scenes_data ?? []);
  readonly totalAudio = this.store.totalAudioDuration;

  readonly selectedSceneData = computed(() => {
    const idx = this.selectedScene();
    const list = this.scenes();
    return idx != null ? list[idx] : null;
  });

  previewImageUrl = computed(() => {
    const scene = this.selectedSceneData();
    if (!scene?.image_path) return null;
    return this.media.mediaUrl(scene.image_path);
  });

  private videoId = '';

  ngOnInit(): void {
    this.videoId = this.route.snapshot.paramMap.get('id') ?? '';
    if (!this.videoId) {
      this.loadError.set('Proyecto no encontrado');
      return;
    }
    this.store.loadVideo(this.videoId);
    this.api.get(this.videoId).subscribe({
      next: (v) => {
        this.store.activeVideo.set(v);
        if (v.status === 'DONE') this.loadPreviewVideo();
      },
      error: () => this.loadError.set('No se pudo cargar el proyecto. ¿Backend activo?'),
    });
  }

  ngOnDestroy(): void {
    if (this.previewVideoUrl()) {
      URL.revokeObjectURL(this.previewVideoUrl()!);
    }
  }

  statusMessage(): string {
    const v = this.video();
    if (!v) return '';
    if (v.status === 'FAILED') return v.error_message || 'Generación fallida';
    if (v.status === 'DONE') return 'Procesando preview…';
    return `Generando… ${v.pipeline_state || v.status}`;
  }

  private loadPreviewVideo(): void {
    this.api.getDownloadUrl(this.videoId).subscribe({
      next: (res) => {
        const url = res.download_url.startsWith('http')
          ? res.download_url
          : `${environment.apiBaseUrl}${res.download_url}`;
        this.previewVideoUrl.set(url);
      },
    });
  }

  download(): void {
    const v = this.video();
    if (!v) return;
    this.api.getDownloadUrl(v.id).subscribe({
      next: (res) => {
        this.api.downloadBlob(res.download_url).subscribe((blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = res.filename || `video-${v.id}.mp4`;
          a.click();
          URL.revokeObjectURL(url);
        });
      },
      error: () => this.notifications.error('Descarga no disponible aún'),
    });
  }

  retry(): void {
    const v = this.video();
    if (!v) return;
    this.api.retry(v.id).subscribe({
      next: () => {
        this.notifications.success('Generación reiniciada');
        this.store.loadVideo(v.id);
        this.previewVideoUrl.set(null);
      },
      error: (err) =>
        this.notifications.error('Error', err?.error?.detail || 'No se pudo reintentar'),
    });
  }

  persistScenes(scenes: SceneData[]): void {
    const v = this.video();
    if (!v) return;
    this.api.update(v.id, { scenes_data: scenes }).subscribe({
      next: (updated) => {
        this.store.activeVideo.set(updated);
        this.notifications.success('Escenas guardadas');
      },
      error: () => this.notifications.error('No se pudieron guardar las escenas'),
    });
  }
}
