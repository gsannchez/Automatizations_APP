import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'av-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="av-empty">
      <div class="av-empty__icon">{{ icon }}</div>
      <h4 class="av-empty__title">{{ title }}</h4>
      @if (description) {
        <p class="av-empty__desc">{{ description }}</p>
      }
      <div class="av-empty__actions">
        <ng-content />
      </div>
    </div>
  `,
  styles: [
    `
      .av-empty {
        text-align: center;
        padding: 2.5rem 1.5rem;
        color: var(--text-muted);
      }
      .av-empty__icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        opacity: 0.7;
      }
      .av-empty__title {
        color: var(--text-main);
        font-size: 0.9375rem;
        margin: 0 0 0.35rem;
      }
      .av-empty__desc {
        font-size: 0.8125rem;
        max-width: 320px;
        margin: 0 auto 1rem;
      }
      .av-empty__actions {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        flex-wrap: wrap;
      }
    `,
  ],
})
export class AvEmptyStateComponent {
  @Input() title = 'No data';
  @Input() description?: string;
  @Input() icon = '📭';
}
