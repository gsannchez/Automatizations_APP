import { Component, OnInit, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { VideoStore } from '../../core/stores/video.store';
import { SystemStore } from '../../core/stores/system.store';
import { AvCardComponent } from '../../shared/components/ui/av-card.component';
import { AvBadgeComponent } from '../../shared/components/ui/av-badge.component';
import { AvProgressComponent } from '../../shared/components/ui/av-progress.component';
import { AvSkeletonComponent } from '../../shared/components/ui/av-skeleton.component';
import { TERMINAL_STATUSES } from '../../core/constants/pipeline.constants';

@Component({
  selector: 'app-render-monitor',
  standalone: true,
  imports: [CommonModule, RouterModule, AvCardComponent, AvBadgeComponent, AvProgressComponent, AvSkeletonComponent],
  template: `
    <div class="render-mon">
      <header>
        <h1>Render Monitor</h1>
        <p>Cola, trabajos activos y recursos del pipeline</p>
      </header>

      <div class="render-mon__grid">
        <av-card title="Recursos GPU / VRAM">
          @if (gpu(); as g) {
            <av-progress [value]="g.usage_percent ?? 0" label="VRAM" />
            <dl class="metrics">
              <dt>Dispositivo</dt>
              <dd>{{ g.device_name || 'N/A' }}</dd>
              <dt>Usado</dt>
              <dd>{{ g.used_mb ?? 0 }} MB</dd>
              <dt>Libre</dt>
              <dd>{{ g.free_mb ?? 0 }} MB</dd>
            </dl>
          } @else if (systemStore.apiError()) {
            <p class="api-err">{{ systemStore.apiError() }}</p>
          } @else {
            <av-skeleton height="100px" />
          }
        </av-card>

        <av-card title="Cola de contenido" subtitle="Orchestration schedule">
          @if (queue(); as q) {
            <p class="count">Pendientes: <strong>{{ q['pending_count'] ?? 0 }}</strong></p>
            <ul class="queue-list">
              @for (item of queueItems(); track $index) {
                <li>{{ item['trend_topic'] || item['platform'] }} · P{{ item['priority'] }}</li>
              }
            </ul>
          } @else {
            <av-skeleton height="80px" />
          }
        </av-card>

        <av-card title="Trabajos activos" class="span-2">
          <table>
            <thead>
              <tr>
                <th>Proyecto</th>
                <th>Estado</th>
                <th>Progreso</th>
                <th>Pipeline</th>
              </tr>
            </thead>
            <tbody>
              @for (v of activeJobs(); track v.id) {
                <tr>
                  <td><a [routerLink]="['/projects', v.id]">{{ v.title }}</a></td>
                  <td><av-badge variant="warning">{{ v.status }}</av-badge></td>
                  <td><av-progress [value]="v.progress" size="sm" /></td>
                  <td>{{ v.pipeline_state || '—' }}</td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="4" class="muted">No hay renders activos</td>
                </tr>
              }
            </tbody>
          </table>
        </av-card>

        <av-card title="Historial reciente" class="span-2">
          <table>
            <thead>
              <tr>
                <th>Proyecto</th>
                <th>Estado</th>
                <th>Progreso</th>
              </tr>
            </thead>
            <tbody>
              @for (v of historyJobs(); track v.id) {
                <tr>
                  <td>{{ v.title }}</td>
                  <td>
                    <av-badge [variant]="v.status === 'DONE' ? 'success' : 'danger'">{{ v.status }}</av-badge>
                  </td>
                  <td>{{ v.progress }}%</td>
                </tr>
              }
            </tbody>
          </table>
        </av-card>
      </div>
    </div>
  `,
  styles: [
    `
      .render-mon h1 {
        margin: 0;
      }
      .render-mon > header p {
        color: var(--text-muted);
        font-size: 0.875rem;
      }
      .render-mon__grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1.25rem;
      }
      .span-2 {
        grid-column: span 2;
      }
      @media (max-width: 900px) {
        .render-mon__grid,
        .span-2 {
          grid-column: auto;
          grid-template-columns: 1fr;
        }
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8125rem;
      }
      th,
      td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid var(--border);
      }
      th {
        color: var(--text-muted);
        font-size: 0.6875rem;
        text-transform: uppercase;
      }
      .metrics {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 0.25rem 1rem;
        margin-top: 0.75rem;
        font-size: 0.8125rem;
      }
      .queue-list {
        margin: 0.5rem 0 0;
        padding-left: 1.25rem;
        font-size: 0.8125rem;
      }
      .count {
        font-size: 0.875rem;
      }
      .muted {
        color: var(--text-muted);
        text-align: center;
      }
      .api-err {
        color: var(--danger);
        font-size: 0.8125rem;
      }
    `,
  ],
})
export class RenderMonitorComponent implements OnInit {
  private readonly videoStore = inject(VideoStore);
  readonly systemStore = inject(SystemStore);

  readonly gpu = computed(() => this.systemStore.pipelineStatus()?.gpu);
  readonly queue = this.systemStore.queueHealth;

  queueItems = computed(() => {
    const q = this.queue();
    const items = q?.['items'];
    return Array.isArray(items) ? (items as Record<string, unknown>[]) : [];
  });

  activeJobs = computed(() =>
    this.videoStore.videos().filter(
      (v) => !TERMINAL_STATUSES.includes(v.status as (typeof TERMINAL_STATUSES)[number])
    )
  );

  historyJobs = computed(() =>
    this.videoStore
      .videos()
      .filter((v) => TERMINAL_STATUSES.includes(v.status as (typeof TERMINAL_STATUSES)[number]))
      .slice(0, 15)
  );

  ngOnInit(): void {
    this.videoStore.loadList(1, 30);
    this.systemStore.refresh();
  }
}
