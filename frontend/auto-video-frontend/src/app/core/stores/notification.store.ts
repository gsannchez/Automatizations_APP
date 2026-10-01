import { Injectable, signal } from '@angular/core';

export interface AppNotification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
  durationMs?: number;
}

@Injectable({ providedIn: 'root' })
export class NotificationStore {
  readonly items = signal<AppNotification[]>([]);

  show(n: Omit<AppNotification, 'id'>): void {
    const item: AppNotification = { ...n, id: crypto.randomUUID() };
    this.items.update((list) => [...list, item]);
    const ms = n.durationMs ?? 4500;
    setTimeout(() => this.dismiss(item.id), ms);
  }

  dismiss(id: string): void {
    this.items.update((list) => list.filter((x) => x.id !== id));
  }

  success(title: string, message?: string): void {
    this.show({ type: 'success', title, message });
  }

  error(title: string, message?: string): void {
    this.show({ type: 'error', title, message, durationMs: 8000 });
  }

  info(title: string, message?: string): void {
    this.show({ type: 'info', title, message });
  }
}
