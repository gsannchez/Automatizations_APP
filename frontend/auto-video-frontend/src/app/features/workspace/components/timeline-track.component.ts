import { Component, Input, computed, inject, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SceneData } from '../../../core/types/video.types';
import { ApiClientService } from '../../../core/services/api-client.service';
import { AvBadgeComponent } from '../../../shared/components/ui/av-badge.component';

@Component({
  selector: 'av-timeline-track',
  standalone: true,
  imports: [CommonModule, AvBadgeComponent],
  template: `
    <div class="timeline">
      <div class="timeline__ruler">
        <span>0s</span>
        <span>{{ totalDuration() | number: '1.1-1' }}s audio</span>
      </div>
      <div class="timeline__track">
        @for (scene of scenes; track trackScene($index, scene); let i = $index) {
          <div
            class="timeline__scene"
            [style.flex]="sceneWeight(scene)"
            [class.active]="selectedIndex === i"
            (click)="sceneSelect.emit(i)"
          >
            <div class="timeline__scene-inner">
              <span class="timeline__num">S{{ i + 1 }}</span>
              <span class="timeline__dur">{{ scene.duration ?? 0 | number: '1.1-1' }}s</span>
              <av-badge [variant]="sceneBadgeVariant(scene, i)" [dot]="true">
                {{ sceneLabel(scene, i) }}
              </av-badge>
              @if (scene.image_path) {
                <img class="timeline__thumb" [src]="mediaUrl(scene.image_path)" alt="" />
              }
            </div>
          </div>
        } @empty {
          <div class="timeline__empty">Sin escenas — el timeline se generará tras el script</div>
        }
      </div>
      <div class="timeline__legend">
        <span>■ Imagen</span>
        <span>♪ Audio</span>
        <span>◆ Prompt</span>
      </div>
    </div>
  `,
  styles: [
    `
      .timeline {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1rem;
      }
      .timeline__ruler {
        display: flex;
        justify-content: space-between;
        font-size: 0.6875rem;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
      }
      .timeline__track {
        display: flex;
        gap: 4px;
        min-height: 72px;
        align-items: stretch;
      }
      .timeline__scene {
        min-width: 48px;
        cursor: pointer;
        border-radius: var(--radius-sm);
        overflow: hidden;
        border: 2px solid transparent;
        transition: border-color 0.15s;
      }
      .timeline__scene.active {
        border-color: var(--primary);
      }
      .timeline__scene-inner {
        height: 100%;
        background: var(--bg-hover);
        padding: 0.35rem;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        font-size: 0.625rem;
      }
      .timeline__num {
        font-weight: 700;
        color: var(--text-main);
      }
      .timeline__dur {
        color: var(--text-muted);
      }
      .timeline__thumb {
        width: 100%;
        height: 28px;
        object-fit: cover;
        border-radius: 3px;
        margin-top: auto;
      }
      .timeline__empty {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        font-size: 0.8125rem;
      }
      .timeline__legend {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.6875rem;
        color: var(--text-muted);
      }
    `,
  ],
})
export class TimelineTrackComponent {
  @Input({ required: true }) scenes: SceneData[] = [];
  @Input() selectedIndex: number | null = null;
  @Input() sceneProgress: Record<string, { image?: string; audio?: string }> | null = null;

  sceneSelect = output<number>();

  private readonly api = inject(ApiClientService);

  totalDuration = computed(() =>
    this.scenes.reduce((s, sc) => s + (sc.duration ?? 0), 0)
  );

  trackScene(i: number, _s: SceneData): number {
    return i;
  }

  sceneWeight(scene: SceneData): string {
    const d = scene.duration ?? 1;
    return String(Math.max(d, 0.5));
  }

  mediaUrl(path: string): string | null {
    return this.api.mediaUrl(path);
  }

  sceneLabel(scene: SceneData, index: number): string {
    const img = this.sceneProgress?.[String(index)]?.image;
    const aud = this.sceneProgress?.[String(index)]?.audio;
    if (scene.status === 'READY' || (img === 'done' && aud === 'done')) return 'READY';
    if (aud === 'done') return 'AUDIO';
    if (img === 'done') return 'IMAGE';
    return scene.status || 'PENDING';
  }

  sceneBadgeVariant(scene: SceneData, index: number): 'success' | 'warning' | 'neutral' {
    const label = this.sceneLabel(scene, index);
    if (label === 'READY') return 'success';
    if (label === 'AUDIO' || label === 'IMAGE') return 'warning';
    return 'neutral';
  }
}
