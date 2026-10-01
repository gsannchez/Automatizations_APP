import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AvBadgeComponent } from '../../../shared/components/ui/av-badge.component';
import {
  getVisualSteps,
  visualStepLabel,
  visualStepStatus,
} from '../../../core/utils/pipeline.util';

@Component({
  selector: 'av-pipeline-visualizer',
  standalone: true,
  imports: [CommonModule, AvBadgeComponent],
  template: `
    <div class="pipeline-viz">
      @for (step of steps; track step.id; let last = $last) {
        @let st = stepState(step.states);
        <div
          class="pipeline-viz__step"
          [class.active]="st === 'active'"
          [class.done]="st === 'done'"
          [class.failed]="st === 'failed'"
        >
          <div class="pipeline-viz__node">
            <span class="pipeline-viz__label">{{ step.label }}</span>
            <av-badge [variant]="badgeVariant(st)" [dot]="true">
              {{ getStepLabel(st) }}
            </av-badge>
          </div>
          @if (!last) {
            <div class="pipeline-viz__arrow">↓</div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .pipeline-viz__step {
        opacity: 0.5;
        transition: opacity 0.2s;
      }
      .pipeline-viz__step.active,
      .pipeline-viz__step.done {
        opacity: 1;
      }
      .pipeline-viz__step.failed .pipeline-viz__node {
        border-color: var(--danger);
      }
      .pipeline-viz__node {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0.75rem;
        background: var(--bg-hover);
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
      }
      .pipeline-viz__step.active .pipeline-viz__node {
        border-color: var(--primary);
        background: var(--primary-light);
      }
      .pipeline-viz__label {
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--text-main);
      }
      .pipeline-viz__arrow {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.875rem;
        padding: 0.15rem 0;
      }
    `,
  ],
})
export class PipelineVisualizerComponent {
  @Input() pipelineState: string | null = null;
  @Input() progress = 0;
  @Input() errorMessage: string | null = null;

  readonly steps = getVisualSteps();
  protected readonly getStepLabel = visualStepLabel;

  stepState(states: readonly string[]) {
    return visualStepStatus(states, this.pipelineState, !!this.errorMessage);
  }

  badgeVariant(st: ReturnType<typeof visualStepStatus>): 'success' | 'warning' | 'danger' | 'neutral' {
    if (st === 'failed') return 'danger';
    if (st === 'active') return 'warning';
    if (st === 'done') return 'success';
    return 'neutral';
  }
}
