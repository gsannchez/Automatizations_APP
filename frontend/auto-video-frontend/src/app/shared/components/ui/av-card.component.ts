import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'av-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="av-card" [class.av-card--flush]="flush">
      @if (title || subtitle) {
        <div class="av-card__header">
          @if (title) {
            <h3 class="av-card__title">{{ title }}</h3>
          }
          @if (subtitle) {
            <p class="av-card__subtitle">{{ subtitle }}</p>
          }
          <div class="av-card__actions">
            <ng-content select="[cardActions]" />
          </div>
        </div>
      }
      <div class="av-card__body">
        <ng-content />
      </div>
    </div>
  `,
  styles: [
    `
      .av-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xs);
        overflow: hidden;
      }
      .av-card--flush .av-card__body {
        padding: 0;
      }
      .av-card__header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--border);
      }
      .av-card__title {
        font-size: 0.9375rem;
        font-weight: 600;
        margin: 0;
      }
      .av-card__subtitle {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin: 0.25rem 0 0;
      }
      .av-card__actions {
        margin-left: auto;
      }
      .av-card__body {
        padding: 1.25rem;
      }
    `,
  ],
})
export class AvCardComponent {
  @Input() title?: string;
  @Input() subtitle?: string;
  @Input() flush = false;
}
