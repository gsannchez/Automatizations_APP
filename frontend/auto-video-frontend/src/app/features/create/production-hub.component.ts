import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import {
  getProductionTypesByCategory,
  ProductionCategory,
} from '../../core/constants/production-types.constants';
import { AvBadgeComponent } from '../../shared/components/ui/av-badge.component';

@Component({
  selector: 'app-production-hub',
  standalone: true,
  imports: [CommonModule, RouterModule, AvBadgeComponent],
  template: `
    <div class="hub">
      <header class="hub__header">
        <div>
          <h1>Estudio de producción</h1>
          <p>Elige el formato — cada uno usa un pipeline distinto del backend.</p>
        </div>
      </header>

      @for (cat of categories; track cat.key) {
        <section class="hub__section">
          <h2>{{ cat.label }}</h2>
          <p class="hub__section-desc">{{ cat.description }}</p>
          <div class="hub__grid">
            @for (item of byCategory(cat.key); track item.id) {
              <a
                class="hub__card av-surface"
                [routerLink]="item.route"
                [queryParams]="item.queryParams"
              >
                @if (item.featured) {
                  <av-badge variant="info">Popular</av-badge>
                }
                <span class="hub__icon">{{ item.icon }}</span>
                <h3>{{ item.name }}</h3>
                <p>{{ item.description }}</p>
                <div class="hub__tags">
                  @for (tag of item.tags; track tag) {
                    <span class="tag">{{ tag }}</span>
                  }
                </div>
              </a>
            }
          </div>
        </section>
      }
    </div>
  `,
  styles: [
    `
      .hub__header {
        margin-bottom: 2rem;
      }
      .hub__header h1 {
        margin: 0;
        font-size: 1.5rem;
      }
      .hub__header p {
        color: var(--text-muted);
        margin-top: 0.35rem;
      }
      .hub__section {
        margin-bottom: 2rem;
      }
      .hub__section h2 {
        font-size: 1.125rem;
        margin: 0 0 0.25rem;
      }
      .hub__section-desc {
        color: var(--text-muted);
        font-size: 0.8125rem;
        margin-bottom: 1rem;
      }
      .hub__grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 1rem;
      }
      .hub__card {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 1.25rem;
        border-radius: var(--radius-lg);
        text-decoration: none;
        color: inherit;
        transition:
          border-color 0.15s,
          box-shadow 0.15s,
          transform 0.15s;
      }
      .hub__card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
      }
      .hub__icon {
        font-size: 1.75rem;
      }
      .hub__card h3 {
        margin: 0;
        font-size: 1rem;
      }
      .hub__card p {
        margin: 0;
        font-size: 0.8125rem;
        color: var(--text-secondary);
        line-height: 1.45;
        flex: 1;
      }
      .hub__tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-top: 0.35rem;
      }
      .tag {
        font-size: 0.625rem;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        background: var(--bg-hover);
        color: var(--text-muted);
        font-weight: 600;
      }
    `,
  ],
})
export class ProductionHubComponent {
  readonly categories: { key: ProductionCategory; label: string; description: string }[] = [
    {
      key: 'ai_short',
      label: 'Shorts generados con IA',
      description: 'Pipeline Audio-First: guion → audio → timeline → imágenes → FFmpeg.',
    },
  ];

  byCategory(cat: ProductionCategory) {
    return getProductionTypesByCategory(cat);
  }
}
