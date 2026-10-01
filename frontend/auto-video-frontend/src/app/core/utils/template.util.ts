import { Template } from '../../services/template.service';

/** Orden alfabético por nombre. */
export function sortTemplates(templates: Template[]): Template[] {
  return [...templates].sort((a, b) => a.name.localeCompare(b.name, 'es', { sensitivity: 'base' }));
}
