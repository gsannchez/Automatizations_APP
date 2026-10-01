import { Component, HostListener, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

interface Command {
  id: string;
  label: string;
  shortcut?: string;
  action: () => void;
}

@Component({
  selector: 'av-command-palette',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (open()) {
      <div class="palette-backdrop" (click)="close()">
        <div class="palette" (click)="$event.stopPropagation()">
          <input
            #searchInput
            type="text"
            placeholder="Buscar comandos… (Ctrl+K)"
            [value]="query()"
            (input)="onQuery($event)"
          />
          <ul>
            @for (cmd of filtered(); track cmd.id) {
              <li (click)="run(cmd)">
                <span>{{ cmd.label }}</span>
                @if (cmd.shortcut) {
                  <kbd>{{ cmd.shortcut }}</kbd>
                }
              </li>
            }
          </ul>
        </div>
      </div>
    }
  `,
  styles: [
    `
      .palette-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 15vh;
      }
      .palette {
        width: 100%;
        max-width: 520px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        overflow: hidden;
      }
      .palette input {
        width: 100%;
        padding: 1rem 1.25rem;
        border: none;
        border-bottom: 1px solid var(--border);
        font-size: 1rem;
        background: transparent;
        color: var(--text-main);
        outline: none;
      }
      .palette ul {
        list-style: none;
        max-height: 320px;
        overflow-y: auto;
        margin: 0;
        padding: 0.5rem;
      }
      .palette li {
        display: flex;
        justify-content: space-between;
        padding: 0.6rem 0.75rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-size: 0.875rem;
      }
      .palette li:hover {
        background: var(--bg-hover);
      }
      kbd {
        font-size: 0.6875rem;
        color: var(--text-muted);
        background: var(--bg-hover);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
      }
    `,
  ],
})
export class CommandPaletteComponent {
  private readonly router = inject(Router);

  readonly open = signal(false);
  readonly query = signal('');

  private readonly commands: Command[] = [
    { id: 'dash', label: 'Ir al Dashboard', action: () => this.router.navigate(['/dashboard']) },
    { id: 'create', label: 'Estudio de producción (formatos)', action: () => this.router.navigate(['/create']) },
    { id: 'videos', label: 'Proyectos / Videos', action: () => this.router.navigate(['/videos']) },
    { id: 'new', label: 'Nuevo short IA', shortcut: 'N', action: () => this.router.navigate(['/videos/new']) },
    { id: 'render', label: 'Render Monitor', action: () => this.router.navigate(['/render']) },
    { id: 'assets', label: 'Asset Library', action: () => this.router.navigate(['/assets']) },
    { id: 'logs', label: 'Log Console', action: () => this.router.navigate(['/logs']) },
    { id: 'settings', label: 'Settings', action: () => this.router.navigate(['/settings']) },
  ];

  filtered = () => {
    const q = this.query().toLowerCase();
    return this.commands.filter((c) => c.label.toLowerCase().includes(q));
  };

  @HostListener('document:keydown', ['$event'])
  onKey(ev: KeyboardEvent): void {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === 'k') {
      ev.preventDefault();
      this.open.set(!this.open());
    }
    if (ev.key === 'Escape') this.close();
  }

  onQuery(ev: Event): void {
    this.query.set((ev.target as HTMLInputElement).value);
  }

  run(cmd: Command): void {
    cmd.action();
    this.close();
  }

  close(): void {
    this.open.set(false);
    this.query.set('');
  }
}
