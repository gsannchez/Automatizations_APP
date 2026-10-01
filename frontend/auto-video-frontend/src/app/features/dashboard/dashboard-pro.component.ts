import { Component, OnInit, inject, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { VideoStore } from '../../core/stores/video.store';
import { SystemStore } from '../../core/stores/system.store';
import { AuthStats } from '../../core/types/auth.types';
import { AvCardComponent } from '../../shared/components/ui/av-card.component';
import { AvBadgeComponent } from '../../shared/components/ui/av-badge.component';
import { AvSkeletonComponent } from '../../shared/components/ui/av-skeleton.component';
import { AvButtonComponent } from '../../shared/components/ui/av-button.component';
import { AvProgressComponent } from '../../shared/components/ui/av-progress.component';
import { getFeaturedProductionTypes } from '../../core/constants/production-types.constants';

@Component({
  selector: 'app-dashboard-pro',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    AvCardComponent,
    AvBadgeComponent,
    AvSkeletonComponent,
    AvButtonComponent,
    AvProgressComponent,
  ],
  template: `
    <div class="dash">
      <header class="dash__hero">
        <div>
          <h1>Studio Dashboard</h1>
          <p>Pipeline Audio-First · producción en tiempo real</p>
        </div>
        <av-button routerLink="/create">Crear contenido</av-button>
      </header>

      @if (stats(); as s) {
        <div class="dash__stats">
          <av-card>
            <div class="stat">
              <span class="stat__label">Videos</span>
              <span class="stat__value">{{ s.total_videos }}</span>
            </div>
          </av-card>
          <av-card>
            <div class="stat">
              <span class="stat__label">En proceso</span>
              <span class="stat__value">{{ s.processing_videos }}</span>
            </div>
          </av-card>
          <av-card>
            <div class="stat">
              <span class="stat__label">Canales</span>
              <span class="stat__value">{{ s.active_channels }}</span>
            </div>
          </av-card>
          <av-card>
            <div class="stat">
              <span class="stat__label">Plan</span>
              <span class="stat__value">{{ s.plan }}</span>
            </div>
          </av-card>
        </div>
      } @else {
        <av-skeleton height="80px" />
      }

      <av-card title="Formatos de producción" subtitle="Shorts IA y estilos virales">
        <div class="format-quick">
          @for (f of featuredFormats; track f.id) {
            <a class="format-quick__item" [routerLink]="f.route" [queryParams]="f.queryParams">
              <span>{{ f.icon }}</span>
              <strong>{{ f.name }}</strong>
            </a>
          }
          <a class="format-quick__all" routerLink="/create">Ver todos →</a>
        </div>
      </av-card>

      <div class="dash__grid">
        <av-card title="Estado del sistema" subtitle="API · Redis · Celery · GPU">
          @if (systemStore.apiError(); as err) {
            <p class="api-err">{{ err }}</p>
          }
          @if (pipeline(); as p) {
            <div class="sys-row">
              <span>API / Pipeline</span>
              <av-badge [variant]="statusVariant(p.pipeline.status)">{{ p.pipeline.status }}</av-badge>
            </div>
            <div class="sys-row">
              <span>Celery workers</span>
              <av-badge [variant]="p.pipeline.celery?.available ? 'success' : 'danger'">
                {{ p.pipeline.celery?.available ? 'Online' : 'Offline' }}
              </av-badge>
            </div>
            <div class="sys-row">
              <span>GPU VRAM</span>
              <span>{{ p.gpu.usage_percent ?? 0 | number: '1.0-0' }}%</span>
            </div>
            <av-progress [value]="p.gpu.usage_percent ?? 0" label="Uso GPU" size="sm" />
            <div class="sys-row">
              <span>ComfyUI</span>
              <av-badge [variant]="p.comfyui.reachable ? 'success' : 'warning'">
                {{ p.comfyui.reachable ? 'OK' : 'Unreachable' }}
              </av-badge>
            </div>
            <div class="sys-row">
              <span>Calidad</span>
              <span>{{ p.pipeline.quality_tier || '—' }}</span>
            </div>
          } @else {
            <av-skeleton height="120px" />
          }
        </av-card>

        <av-card title="Renderizaciones recientes">
          <div class="video-list">
            @for (v of recentVideos(); track v.id) {
              <a [routerLink]="['/projects', v.id]" class="video-item">
                <div>
                  <strong>{{ v.title }}</strong>
                  <small>{{ v.pipeline_state || v.status }}</small>
                </div>
                <av-progress [value]="v.progress" size="sm" />
              </a>
            } @empty {
              <p class="muted">Sin proyectos recientes</p>
            }
          </div>
          <av-button variant="ghost" routerLink="/videos">Ver todos</av-button>
        </av-card>
      </div>
    </div>
  `,
  styles: [
    `
      .dash {
        animation: fadeUp 0.35s ease;
      }
      .dash__hero {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
      }
      .dash__hero h1 {
        font-size: 1.5rem;
        margin: 0;
      }
      .dash__hero p {
        color: var(--text-muted);
        font-size: 0.875rem;
        margin-top: 0.25rem;
      }
      .dash__stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
      }
      @media (max-width: 900px) {
        .dash__stats {
          grid-template-columns: repeat(2, 1fr);
        }
      }
      .stat__label {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      .stat__value {
        font-size: 1.5rem;
        font-weight: 700;
        display: block;
      }
      .dash__grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
      }
      @media (max-width: 900px) {
        .dash__grid {
          grid-template-columns: 1fr;
        }
      }
      .sys-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.35rem 0;
        font-size: 0.8125rem;
      }
      .video-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-bottom: 1rem;
      }
      .video-item {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        padding: 0.5rem;
        border-radius: var(--radius-md);
        text-decoration: none;
        color: inherit;
        border: 1px solid transparent;
      }
      .video-item:hover {
        background: var(--bg-hover);
        border-color: var(--border);
      }
      .video-item small {
        color: var(--text-muted);
        font-size: 0.6875rem;
      }
      .muted {
        color: var(--text-muted);
        font-size: 0.8125rem;
      }
      .api-err {
        color: var(--danger);
        font-size: 0.8125rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        background: var(--danger-bg);
        border-radius: var(--radius-sm);
      }
      .format-quick {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
      }
      .format-quick__item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        text-decoration: none;
        color: inherit;
        font-size: 0.8125rem;
      }
      .format-quick__item:hover {
        border-color: var(--primary);
        background: var(--bg-hover);
      }
      .format-quick__all {
        font-size: 0.8125rem;
        font-weight: 600;
        margin-left: auto;
      }
    `,
  ],
})
export class DashboardProComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly videoStore = inject(VideoStore);
  readonly systemStore = inject(SystemStore);

  readonly stats = signal<AuthStats | null>(null);
  readonly pipeline = this.systemStore.pipelineStatus;
  readonly recentVideos = computed(() => this.videoStore.videos().slice(0, 5));
  readonly featuredFormats = getFeaturedProductionTypes();

  ngOnInit(): void {
    this.auth.getStats().subscribe({
      next: (s) => this.stats.set(s),
      error: () => this.stats.set({ total_videos: 0, active_channels: 0, total_templates: 0, processing_videos: 0, plan: '—' }),
    });
    this.videoStore.loadList(1, 8);
    this.systemStore.refresh();
  }

  statusVariant(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
    if (status === 'healthy') return 'success';
    if (status === 'critical') return 'danger';
    return 'warning';
  }
}
