import { PIPELINE_STAGES, PIPELINE_VISUAL_STEPS } from '../constants/pipeline.constants';

/** Ordered pipeline keys for progress comparison */
const ORDERED_STATES = PIPELINE_STAGES.map((s) => s.key);

export function pipelineStateIndex(state: string | null | undefined): number {
  if (!state) return -1;
  if (state === 'DONE') return ORDERED_STATES.length;
  if (state === 'FAILED') return -1;
  const idx = ORDERED_STATES.indexOf(state as (typeof ORDERED_STATES)[number]);
  return idx >= 0 ? idx : -1;
}

export function isStateAtOrPast(current: string | null | undefined, target: string): boolean {
  const cur = pipelineStateIndex(current);
  const tgt = pipelineStateIndex(target);
  if (cur < 0 || tgt < 0) return false;
  return cur >= tgt;
}

export function visualStepStatus(
  stepStates: readonly string[],
  pipelineState: string | null | undefined,
  failed: boolean
): 'pending' | 'active' | 'done' | 'failed' {
  if (failed) return 'failed';
  const current = pipelineState ?? '';
  if (stepStates.includes(current)) return 'active';
  const stepMax = Math.max(...stepStates.map((s) => pipelineStateIndex(s)));
  const curIdx = pipelineStateIndex(current);
  if (curIdx > stepMax) return 'done';
  if (current === 'DONE') return 'done';
  return 'pending';
}

export function visualStepLabel(status: ReturnType<typeof visualStepStatus>): string {
  switch (status) {
    case 'active':
      return 'En curso';
    case 'done':
      return 'Completado';
    case 'failed':
      return 'Error';
    default:
      return 'Pendiente';
  }
}

export function getVisualSteps() {
  return PIPELINE_VISUAL_STEPS;
}
