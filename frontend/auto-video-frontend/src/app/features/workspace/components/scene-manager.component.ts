import { Component, Input, output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SceneData } from '../../../core/types/video.types';
import { ApiClientService } from '../../../core/services/api-client.service';
import { AvCardComponent } from '../../../shared/components/ui/av-card.component';
import { AvBadgeComponent } from '../../../shared/components/ui/av-badge.component';
import { AvButtonComponent } from '../../../shared/components/ui/av-button.component';

@Component({
  selector: 'av-scene-manager',
  standalone: true,
  imports: [CommonModule, AvCardComponent, AvBadgeComponent, AvButtonComponent],
  template: `
    <av-card title="Escenas" [subtitle]="scenes.length ? scenes.length + ' en timeline' : 'Sin escenas aún'">
      <div class="scenes">
        @for (scene of scenes; track $index; let i = $index) {
          <article
            class="scene-row"
            [class.selected]="selectedIndex === i"
            (click)="select.emit(i)"
          >
            <div class="scene-row__head">
              <span class="scene-num">#{{ i + 1 }}</span>
              <av-badge [variant]="badgeFor(scene)">{{ scene.status || 'PENDING' }}</av-badge>
              <span class="scene-dur">{{ scene.duration ?? '—' }}s</span>
            </div>
            <div class="scene-assets">
              @if (progressFor(i, 'image') === 'done') {
                <span class="chip chip--ok">Imagen ✓</span>
              }
              @if (progressFor(i, 'audio') === 'done') {
                <span class="chip chip--ok">Audio ✓</span>
              }
            </div>
            <p class="scene-text">{{ scene.text || scene.voiceover_text || '—' }}</p>
            @if (scene.image_prompt) {
              <p class="scene-prompt">{{ scene.image_prompt }}</p>
            }
            @if (scene.image_path) {
              <img class="scene-img" [src]="mediaUrl(scene.image_path)" alt="" />
            }
          </article>
        } @empty {
          <p class="muted">El pipeline creará escenas tras el guion (SCRIPTING).</p>
        }
      </div>
      @if (scenes.length) {
        <div class="scene-actions">
          <av-button size="sm" variant="secondary" (click)="regenerate.emit(0)">Reintentar pipeline</av-button>
        </div>
      }
    </av-card>
  `,
  styles: [
    `
      .scenes {
        max-height: 380px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      }
      .scene-row {
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.65rem;
        cursor: pointer;
      }
      .scene-row.selected {
        border-color: var(--primary);
        background: var(--primary-light);
      }
      .scene-row__head {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.25rem;
      }
      .scene-num {
        font-weight: 700;
        font-size: 0.8125rem;
      }
      .scene-dur {
        margin-left: auto;
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      .scene-assets {
        display: flex;
        gap: 0.35rem;
        margin-bottom: 0.25rem;
      }
      .chip {
        font-size: 0.625rem;
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        background: var(--bg-hover);
        color: var(--text-muted);
      }
      .chip--ok {
        background: var(--success-bg);
        color: var(--success);
      }
      .scene-text,
      .scene-prompt {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin: 0.2rem 0;
      }
      .scene-img {
        width: 100%;
        max-height: 80px;
        object-fit: cover;
        border-radius: var(--radius-sm);
        margin-top: 0.35rem;
      }
      .scene-actions {
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border);
      }
      .muted {
        color: var(--text-muted);
        font-size: 0.8125rem;
      }
    `,
  ],
})
export class SceneManagerComponent {
  @Input({ required: true }) scenes: SceneData[] = [];
  @Input() sceneProgress: Record<string, { image?: string; audio?: string }> | null = null;
  @Input() selectedIndex: number | null = null;

  select = output<number>();
  regenerate = output<number>();
  saveScenes = output<SceneData[]>();

  private readonly api = inject(ApiClientService);

  mediaUrl(path: string): string | null {
    return this.api.mediaUrl(path);
  }

  progressFor(index: number, kind: 'image' | 'audio'): string | undefined {
    const key = String(index);
    return this.sceneProgress?.[key]?.[kind];
  }

  badgeFor(scene: SceneData): 'success' | 'warning' | 'neutral' {
    if (scene.status === 'READY') return 'success';
    if (scene.status === 'AUDIO_GENERATED') return 'warning';
    return 'neutral';
  }
}
