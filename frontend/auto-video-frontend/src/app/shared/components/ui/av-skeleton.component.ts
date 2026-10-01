import { Component, Input } from '@angular/core';

@Component({
  selector: 'av-skeleton',
  standalone: true,
  template: `<div class="av-skeleton" [style.width]="width" [style.height]="height"></div>`,
  styles: [
    `
      .av-skeleton {
        background: linear-gradient(
          90deg,
          var(--bg-hover) 25%,
          var(--border) 50%,
          var(--bg-hover) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.2s infinite;
        border-radius: var(--radius-sm);
      }
      @keyframes shimmer {
        0% {
          background-position: 200% 0;
        }
        100% {
          background-position: -200% 0;
        }
      }
    `,
  ],
})
export class AvSkeletonComponent {
  @Input() width = '100%';
  @Input() height = '1rem';
}
