import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationStore } from '../../../core/stores/notification.store';

@Component({
  selector: 'av-toast-container',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-stack">
      @for (n of store.items(); track n.id) {
        <div class="toast toast--{{ n.type }}" (click)="store.dismiss(n.id)">
          <strong>{{ n.title }}</strong>
          @if (n.message) {
            <span>{{ n.message }}</span>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .toast-stack {
        position: fixed;
        bottom: 1.25rem;
        right: 1.25rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 360px;
      }
      .toast {
        padding: 0.75rem 1rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        background: var(--bg-card);
        box-shadow: var(--shadow-lg);
        cursor: pointer;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        font-size: 0.8125rem;
        animation: fadeUp 0.25s ease;
      }
      .toast strong {
        color: var(--text-main);
      }
      .toast span {
        color: var(--text-secondary);
      }
      .toast--success {
        border-left: 3px solid var(--success);
      }
      .toast--error {
        border-left: 3px solid var(--danger);
      }
      .toast--warning {
        border-left: 3px solid var(--warning);
      }
      .toast--info {
        border-left: 3px solid var(--info);
      }
    `,
  ],
})
export class ToastContainerComponent {
  readonly store = inject(NotificationStore);
}
