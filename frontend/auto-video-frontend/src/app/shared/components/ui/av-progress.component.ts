import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'av-progress',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="av-progress">
      @if (label) {
        <div class="av-progress__label">
          <span>{{ label }}</span>
          <span class="av-progress__value">{{ value }}%</span>
        </div>
      }
      <div class="av-progress__track" [class.av-progress--sm]="size === 'sm'">
        <div class="av-progress__fill" [style.width.%]="value" [class.indeterminate]="indeterminate"></div>
      </div>
    </div>
  `,
  styles: [
    `
      .av-progress__label {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 0.35rem;
      }
      .av-progress__value {
        font-variant-numeric: tabular-nums;
      }
      .av-progress__track {
        height: 8px;
        background: var(--bg-hover);
        border-radius: 4px;
        overflow: hidden;
      }
      .av-progress--sm {
        height: 5px;
      }
      .av-progress__fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), #6366f1);
        border-radius: 4px;
        transition: width 0.35s ease;
      }
      .av-progress__fill.indeterminate {
        width: 40% !important;
        animation: indet 1.2s ease-in-out infinite;
      }
      @keyframes indet {
        0% {
          transform: translateX(-100%);
        }
        100% {
          transform: translateX(350%);
        }
      }
    `,
  ],
})
export class AvProgressComponent {
  @Input() value = 0;
  @Input() label?: string;
  @Input() size: 'sm' | 'md' = 'md';
  @Input() indeterminate = false;
}
