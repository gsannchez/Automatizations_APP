import { Injectable, computed, signal } from '@angular/core';
import { LogEntry } from '../types/system.types';

@Injectable({ providedIn: 'root' })
export class LogStore {
  private readonly maxEntries = 2000;
  readonly entries = signal<LogEntry[]>([]);
  readonly filterCategory = signal<LogEntry['category'] | 'all'>('all');
  readonly searchQuery = signal('');

  readonly filtered = computed(() => {
    const q = this.searchQuery().toLowerCase().trim();
    const cat = this.filterCategory();
    return this.entries().filter((e) => {
      if (cat !== 'all' && e.category !== cat) return false;
      if (!q) return true;
      return e.message.toLowerCase().includes(q) || (e.source?.toLowerCase().includes(q) ?? false);
    });
  });

  push(partial: Omit<LogEntry, 'id' | 'timestamp'>): void {
    const entry: LogEntry = {
      ...partial,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    this.entries.update((list) => {
      const next = [entry, ...list];
      return next.slice(0, this.maxEntries);
    });
  }

  clear(): void {
    this.entries.set([]);
  }

  copyAll(): string {
    return this.filtered()
      .map((e) => `[${e.timestamp.toISOString()}] [${e.category}] ${e.message}`)
      .join('\n');
  }
}
