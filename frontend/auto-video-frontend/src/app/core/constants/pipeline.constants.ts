/** Pipeline states aligned with backend PipelineState enum */
export const PIPELINE_STAGES = [
  { key: 'QUEUED', label: 'Queued', phase: 0 },
  { key: 'SCRIPTING', label: 'Script', phase: 1 },
  { key: 'VALIDATED', label: 'Validated', phase: 2 },
  { key: 'IMAGE_GENERATION', label: 'Images', phase: 6 },
  { key: 'AUDIO_GENERATION', label: 'Audio', phase: 1 },
  { key: 'MEDIA_COMPOSITION', label: 'Composition', phase: 9 },
  { key: 'ENCODING', label: 'FFmpeg', phase: 10 },
  { key: 'UPLOADING', label: 'Upload', phase: 12 },
  { key: 'DONE', label: 'Complete', phase: 12 },
  { key: 'FAILED', label: 'Failed', phase: -1 },
] as const;

export const PIPELINE_VISUAL_STEPS = [
  { id: 'script', label: 'Script', states: ['SCRIPTING', 'VALIDATED'] },
  { id: 'audio', label: 'Audio', states: ['AUDIO_GENERATION'] },
  { id: 'timeline', label: 'Timeline', states: ['VALIDATED'] },
  { id: 'scenes', label: 'Scene Planning', states: ['VALIDATED', 'IMAGE_GENERATION'] },
  { id: 'prompts', label: 'Prompts', states: ['IMAGE_GENERATION'] },
  { id: 'images', label: 'Image Gen', states: ['IMAGE_GENERATION'] },
  { id: 'composition', label: 'Video Assembly', states: ['MEDIA_COMPOSITION'] },
  { id: 'ffmpeg', label: 'FFmpeg Render', states: ['ENCODING'] },
  { id: 'output', label: 'Final Output', states: ['UPLOADING', 'DONE'] },
] as const;

export const TERMINAL_STATUSES = ['DONE', 'FAILED'] as const;

export const SCENE_STATUSES = ['PENDING', 'AUDIO_GENERATED', 'READY'] as const;
