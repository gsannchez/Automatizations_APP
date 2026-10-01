import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'av-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type"
      [disabled]="disabled || loading"
      [class]="'av-btn av-btn--' + variant + ' av-btn--' + size"
      (click)="onClick($event)"
    >
      @if (loading) {
        <span class="av-btn__spinner"></span>
      }
      <ng-content />
    </button>
  `,
  styles: [
    `
      .av-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        border-radius: var(--radius-md);
        font-weight: 500;
        cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.15s ease;
        font-family: inherit;
      }
      .av-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      .av-btn--sm {
        padding: 0.35rem 0.75rem;
        font-size: 0.75rem;
      }
      .av-btn--md {
        padding: 0.5rem 1rem;
        font-size: 0.8125rem;
      }
      .av-btn--lg {
        padding: 0.625rem 1.25rem;
        font-size: 0.875rem;
      }
      .av-btn--primary {
        background: var(--primary);
        color: var(--primary-fg);
      }
      .av-btn--primary:hover:not(:disabled) {
        background: var(--primary-hover);
      }
      .av-btn--secondary {
        background: var(--bg-card);
        border-color: var(--border);
        color: var(--text-main);
      }
      .av-btn--secondary:hover:not(:disabled) {
        background: var(--bg-hover);
      }
      .av-btn--ghost {
        background: transparent;
        color: var(--text-secondary);
      }
      .av-btn--ghost:hover:not(:disabled) {
        background: var(--bg-hover);
      }
      .av-btn--danger {
        background: var(--danger);
        color: #fff;
      }
      .av-btn__spinner {
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: #fff;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
      }
      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }
    `,
  ],
})
export class AvButtonComponent {
  @Input() variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'primary';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() type: 'button' | 'submit' = 'button';
  @Input() disabled = false;
  @Input() loading = false;

  onClick(ev: Event): void {
    if (this.disabled || this.loading) {
      ev.preventDefault();
      ev.stopPropagation();
    }
  }
}
