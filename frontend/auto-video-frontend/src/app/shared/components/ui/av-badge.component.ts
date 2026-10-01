import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'av-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="av-badge" [class]="'av-badge--' + variant">
      @if (dot) {
        <span class="av-badge__dot"></span>
      }
      <ng-content />
    </span>
  `,
  styles: [
    `
      .av-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
      }
      .av-badge__dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: currentColor;
      }
      .av-badge--success {
        background: var(--success-bg);
        color: var(--success);
      }
      .av-badge--warning {
        background: var(--warning-bg);
        color: var(--warning);
      }
      .av-badge--danger {
        background: var(--danger-bg);
        color: var(--danger);
      }
      .av-badge--info {
        background: var(--info-bg);
        color: var(--info);
      }
      .av-badge--neutral {
        background: var(--bg-hover);
        color: var(--text-secondary);
      }
    `,
  ],
})
export class AvBadgeComponent {
  @Input() variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral' = 'neutral';
  @Input() dot = true;
}
