import { Component, OnInit, inject, computed, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { VideoStore } from '../../core/stores/video.store';
import { ApiClientService } from '../../core/services/api-client.service';
import { AvCardComponent } from '../../shared/components/ui/av-card.component';
import { SceneData } from '../../core/types/video.types';

interface AssetItem {
  id: string;
  type: 'image' | 'audio' | 'video' | 'prompt' | 'script';
  name: string;
  previewUrl: string | null;
  projectTitle: string;
  tags: string[];
}

@Component({
  selector: 'app-asset-library',
  standalone: true,
  imports: [CommonModule, FormsModule, AvCardComponent],
  template: `
    <div class="assets">
      <header>
        <h1>Biblioteca de assets</h1>
        <p>Extraídos de tus proyectos reales (escenas y vídeos terminados).</p>
      </header>

      <div class="assets__filters">
        <input type="search" placeholder="Buscar…" [(ngModel)]="search" />
        <select [(ngModel)]="typeFilter">
          <option value="all">Todos</option>
          <option value="image">Imágenes</option>
          <option value="audio">Audio</option>
          <option value="prompt">Prompts</option>
          <option value="script">Scripts</option>
          <option value="video">Vídeos finales</option>
        </select>
      </div>

      <p class="assets__count">{{ filteredAssets().length }} assets · {{ videoStore.videos().length }} proyectos</p>

      <div class="assets__grid">
        @for (a of filteredAssets(); track a.id) {
          <av-card>
            <div class="asset-card">
              @if (a.previewUrl && a.type === 'image') {
                <img [src]="a.previewUrl" alt="" class="asset-thumb" />
              } @else {
                <div class="asset-placeholder">{{ typeIcon(a.type) }}</div>
              }
              <div class="asset-meta">
                <span class="asset-type">{{ a.type }}</span>
                <strong>{{ a.name }}</strong>
                <small>{{ a.projectTitle }}</small>
              </div>
            </div>
          </av-card>
        } @empty {
          <p class="muted">No hay assets. Crea y genera un proyecto primero.</p>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .assets__filters {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0 0.5rem;
      }
      .assets__count {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
      }
      .assets__grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1rem;
      }
      .asset-thumb {
        width: 100%;
        height: 120px;
        object-fit: cover;
        border-radius: var(--radius-sm);
      }
      .asset-placeholder {
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-hover);
        border-radius: var(--radius-sm);
        font-size: 2rem;
      }
      .asset-type {
        font-size: 0.625rem;
        text-transform: uppercase;
        color: var(--text-muted);
      }
      .asset-meta strong {
        display: block;
        font-size: 0.8125rem;
        color: var(--text-main);
      }
      .asset-meta small {
        color: var(--text-muted);
      }
      .muted {
        grid-column: 1 / -1;
        color: var(--text-muted);
      }
    `,
  ],
})
export class AssetLibraryComponent implements OnInit {
  readonly videoStore = inject(VideoStore);
  private readonly api = inject(ApiClientService);

  search = '';
  typeFilter = 'all';
  private readonly allAssets = signal<AssetItem[]>([]);

  constructor() {
    effect(() => {
      const videos = this.videoStore.videos();
      this.allAssets.set(this.buildAssets(videos));
    });
  }

  filteredAssets = computed(() => {
    const q = this.search.toLowerCase();
    return this.allAssets().filter((a) => {
      if (this.typeFilter !== 'all' && a.type !== this.typeFilter) return false;
      if (!q) return true;
      return a.name.toLowerCase().includes(q) || a.projectTitle.toLowerCase().includes(q);
    });
  });

  ngOnInit(): void {
    this.videoStore.loadList(1, 100);
  }

  private buildAssets(videos: { id: string; title: string; platform: string; status: string; scenes_data?: SceneData[] | null; storage_key?: string | null }[]): AssetItem[] {
    const items: AssetItem[] = [];
    for (const v of videos) {
      for (const [i, s] of (v.scenes_data ?? []).entries()) {
        if (s.image_path) {
          items.push({
            id: `${v.id}-img-${i}`,
            type: 'image',
            name: `Escena ${i + 1}`,
            previewUrl: this.api.mediaUrl(s.image_path),
            projectTitle: v.title,
            tags: [v.platform],
          });
        }
        if (s.audio_path) {
          items.push({
            id: `${v.id}-aud-${i}`,
            type: 'audio',
            name: `Audio escena ${i + 1}`,
            previewUrl: this.api.mediaUrl(s.audio_path),
            projectTitle: v.title,
            tags: ['audio'],
          });
        }
        if (s.image_prompt) {
          items.push({
            id: `${v.id}-prompt-${i}`,
            type: 'prompt',
            name: s.image_prompt.slice(0, 48),
            previewUrl: null,
            projectTitle: v.title,
            tags: ['prompt'],
          });
        }
        if (s.text || s.voiceover_text) {
          items.push({
            id: `${v.id}-script-${i}`,
            type: 'script',
            name: `Guión escena ${i + 1}`,
            previewUrl: null,
            projectTitle: v.title,
            tags: ['script'],
          });
        }
      }
      if (v.status === 'DONE') {
        items.push({
          id: `${v.id}-final`,
          type: 'video',
          name: v.title,
          previewUrl: null,
          projectTitle: v.title,
          tags: ['final', v.platform],
        });
      }
    }
    return items;
  }

  typeIcon(type: string): string {
    const map: Record<string, string> = {
      image: '🖼',
      audio: '🔊',
      video: '🎬',
      prompt: '✨',
      script: '📝',
    };
    return map[type] ?? '📁';
  }
}
