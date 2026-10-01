import { Injectable, PLATFORM_ID, computed, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export type ThemeMode = 'light' | 'dark' | 'system';

@Injectable({ providedIn: 'root' })
export class ThemeStore {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly mode = signal<ThemeMode>(this.loadMode());

  readonly resolvedTheme = computed(() => {
    const m = this.mode();
    if (m === 'system' && isPlatformBrowser(this.platformId)) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return m === 'system' ? 'light' : m;
  });

  setMode(mode: ThemeMode): void {
    this.mode.set(mode);
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('av-theme', mode);
      this.applyToDocument();
    }
  }

  toggle(): void {
    const next = this.resolvedTheme() === 'dark' ? 'light' : 'dark';
    this.setMode(next);
  }

  applyToDocument(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    document.documentElement.setAttribute('data-theme', this.resolvedTheme());
  }

  private loadMode(): ThemeMode {
    if (!isPlatformBrowser(this.platformId)) return 'light';
    return (localStorage.getItem('av-theme') as ThemeMode) || 'light';
  }
}
