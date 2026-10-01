import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LogStore } from '../../core/stores/log.store';
import { AvCardComponent } from '../../shared/components/ui/av-card.component';
import { AvButtonComponent } from '../../shared/components/ui/av-button.component';

const CATEGORIES = ['all', 'backend', 'workers', 'comfyui', 'ffmpeg', 'audio', 'timeline', 'system'] as const;

@Component({
  selector: 'app-log-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule, AvCardComponent, AvButtonComponent],
  template: `
    <div class="logs">
      <header>
        <h1>Log Console</h1>
        <p>Eventos en vivo vía SSE + sistema</p>
      </header>

      <av-card>
        <div class="logs__toolbar">
          <input
            type="search"
            placeholder="Buscar logs…"
            [ngModel]="logStore.searchQuery()"
            (ngModelChange)="logStore.searchQuery.set($event)"
          />
          <select
            [ngModel]="logStore.filterCategory()"
            (ngModelChange)="onCategory($event)"
          >
            @for (c of categories; track c) {
              <option [value]="c">{{ c }}</option>
            }
          </select>
          <av-button variant="secondary" size="sm" (click)="copy()">Copiar</av-button>
          <av-button variant="ghost" size="sm" (click)="logStore.clear()">Limpiar</av-button>
        </div>

        <div class="logs__console">
          @for (e of logStore.filtered(); track e.id) {
            <div class="log-line log-line--{{ e.level }}">
              <span class="log-time">{{ e.timestamp | date: 'HH:mm:ss' }}</span>
              <span class="log-cat">[{{ e.category }}]</span>
              <span class="log-msg">{{ e.message }}</span>
            </div>
          } @empty {
            <p class="muted">Sin entradas. Conecta SSE o inicia un render.</p>
          }
        </div>
      </av-card>
    </div>
  `,
  styles: [
    `
      .logs h1 {
        margin: 0;
      }
      .logs > header p {
        color: var(--text-muted);
        font-size: 0.875rem;
      }
      .logs__toolbar {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
      }
      .logs__toolbar input,
      .logs__toolbar select {
        flex: 1;
        min-width: 140px;
        padding: 0.5rem 0.75rem;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        background: var(--bg-input);
        color: var(--text-main);
        font-size: 0.8125rem;
      }
      .logs__console {
        font-family: ui-monospace, 'Cascadia Code', monospace;
        font-size: 0.75rem;
        max-height: 60vh;
        overflow-y: auto;
        background: #0d1117;
        color: #c9d1d9;
        border-radius: var(--radius-md);
        padding: 0.75rem;
      }
      .log-line {
        display: flex;
        gap: 0.5rem;
        padding: 0.15rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      }
      .log-time {
        color: #8b949e;
        flex-shrink: 0;
      }
      .log-cat {
        color: #58a6ff;
        flex-shrink: 0;
      }
      .log-line--error .log-msg {
        color: #f85149;
      }
      .log-line--warn .log-msg {
        color: #d29922;
      }
      .muted {
        color: #8b949e;
        padding: 1rem;
      }
    `,
  ],
})
export class LogViewerComponent {
  readonly logStore = inject(LogStore);
  readonly categories = CATEGORIES;

  onCategory(val: string): void {
    this.logStore.filterCategory.set(val as (typeof CATEGORIES)[number]);
  }

  copy(): void {
    navigator.clipboard?.writeText(this.logStore.copyAll());
  }
}
