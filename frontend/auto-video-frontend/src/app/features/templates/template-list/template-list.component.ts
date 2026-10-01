import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TemplateService, Template } from '../../../services/template.service';
import { sortTemplates } from '../../../core/utils/template.util';
import { VideoStore } from '../../../core/stores/video.store';
import { NotificationStore } from '../../../core/stores/notification.store';

@Component({
  selector: 'app-template-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="container">
      <header class="header">
        <div class="header-text">
          <h1>Plantillas</h1>
          <p>Reglas creativas para generaciones automáticas (API real).</p>
        </div>
        <button type="button" (click)="toggleForm()" class="btn-primary">
          {{ showForm ? 'Cancelar' : '+ Nueva plantilla' }}
        </button>
      </header>

      @if (showForm) {
        <div class="form-section">
          <div class="card av-surface">
            <form [formGroup]="templateForm" (ngSubmit)="onSubmit()">
              <div class="form-grid">
                <div class="field">
                  <label>Nombre</label>
                  <input type="text" formControlName="name" placeholder="Ej. Tech Shorts diario" />
                </div>
                <div class="field">
                  <label>Plataforma</label>
                  <select formControlName="platform">
                    <option value="TIKTOK">TikTok</option>
                    <option value="REELS">Reels</option>
                    <option value="SHORTS">YouTube Shorts</option>
                  </select>
                </div>
                <div class="field">
                  <label>Duración recomendada (s)</label>
                  <input type="number" formControlName="recommended_duration" min="15" max="180" />
                </div>
                <div class="field full">
                  <label>Descripción</label>
                  <input type="text" formControlName="description" />
                </div>
                <div class="field full">
                  <label>Prompt para la IA</label>
                  <textarea formControlName="prompt_template" rows="4"></textarea>
                </div>
              </div>
              <div class="form-footer">
                <button type="button" class="btn-ghost" (click)="toggleForm()">Descartar</button>
                <button type="submit" class="btn-primary" [disabled]="templateForm.invalid">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      }

      <div class="templates-grid">
        @for (template of templates; track template.id) {
          <div class="template-card av-surface">
            <div class="template-body">
              <div class="template-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description || 'Sin descripción' }}</p>
                <span class="plat">{{ template.platform }}</span>
              </div>
            </div>
            <div class="template-meta av-surface-muted">
              <div class="meta-item">
                <span class="m-label">Duración</span>
                <span class="m-value">{{ durationLabel(template) }}s</span>
              </div>
              <div class="meta-item">
                <span class="m-label">Uso</span>
                <span class="m-value">{{ usageCount(template.id) }} videos</span>
              </div>
              <button type="button" class="btn-icon" (click)="deleteTemplate(template.id)" title="Eliminar">
                Eliminar
              </button>
            </div>
          </div>
        } @empty {
          <div class="empty-state av-surface">
            <h3>Sin plantillas</h3>
            <p>Crea la primera plantilla para generar vídeos.</p>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .container {
        max-width: 1000px;
        margin: 0 auto;
        animation: fadeUp 0.3s ease-out;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
      }
      .header h1 {
        margin: 0;
        font-size: 1.5rem;
      }
      .header p {
        color: var(--text-muted);
        margin-top: 0.25rem;
      }
      .form-section {
        margin-bottom: 1.5rem;
      }
      .card {
        padding: 1.25rem;
        border-radius: var(--radius-lg);
      }
      .form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
      }
      .full {
        grid-column: 1 / -1;
      }
      .field label {
        display: block;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.35rem;
      }
      .form-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
      }
      .templates-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;
      }
      .template-card {
        border-radius: var(--radius-lg);
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      .template-body {
        padding: 1rem;
      }
      .template-info h4 {
        margin: 0 0 0.25rem;
      }
      .template-info p {
        font-size: 0.8125rem;
        color: var(--text-muted);
        margin: 0;
      }
      .plat {
        display: inline-block;
        margin-top: 0.5rem;
        font-size: 0.6875rem;
        font-weight: 600;
        color: var(--primary);
      }
      .template-meta {
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border-top: 1px solid var(--border);
      }
      .meta-item {
        display: flex;
        flex-direction: column;
      }
      .m-label {
        font-size: 0.625rem;
        color: var(--text-muted);
        text-transform: uppercase;
      }
      .m-value {
        font-size: 0.8125rem;
        font-weight: 600;
      }
      .btn-icon {
        margin-left: auto;
        background: transparent;
        border: 1px solid var(--border);
        padding: 0.35rem 0.6rem;
        border-radius: var(--radius-sm);
        color: var(--danger);
        font-size: 0.75rem;
        cursor: pointer;
      }
      .empty-state {
        grid-column: 1 / -1;
        text-align: center;
        padding: 2.5rem;
        border-radius: var(--radius-lg);
      }
      .btn-primary {
        background: var(--primary);
        color: var(--primary-fg);
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        border: none;
        cursor: pointer;
      }
      .btn-ghost {
        background: transparent;
        color: var(--text-secondary);
        padding: 0.5rem 1rem;
        border: none;
        cursor: pointer;
      }
    `,
  ],
})
export class TemplateListComponent implements OnInit {
  private readonly templateService = inject(TemplateService);
  private readonly videoStore = inject(VideoStore);
  private readonly notifications = inject(NotificationStore);
  private readonly fb = inject(FormBuilder);

  templates: Template[] = [];
  showForm = false;
  templateForm: FormGroup;

  private readonly videos = this.videoStore.videos;

  usageCount = (templateId: string) =>
    this.videos().filter((v) => v.template_id === templateId).length;

  constructor() {
    this.templateForm = this.fb.group({
      name: ['', Validators.required],
      platform: ['TIKTOK', Validators.required],
      description: [''],
      recommended_duration: [60, [Validators.required, Validators.min(15)]],
      prompt_template: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    this.loadTemplates();
    this.videoStore.loadList(1, 100);
  }

  durationLabel(t: Template): number {
    return t.recommended_duration ?? (t.style_config?.['duration'] as number) ?? 60;
  }

  loadTemplates(): void {
    this.templateService.getTemplates().subscribe({
      next: (data) => (this.templates = sortTemplates(data)),
      error: () => this.notifications.error('No se pudieron cargar plantillas'),
    });
  }

  toggleForm(): void {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.templateForm.reset({ platform: 'TIKTOK', recommended_duration: 60 });
    }
  }

  onSubmit(): void {
    if (!this.templateForm.valid) return;
    const v = this.templateForm.value;
    const payload = {
      name: v.name,
      platform: v.platform,
      description: v.description,
      recommended_duration: v.recommended_duration,
      style_config: { prompt_template: v.prompt_template },
    };
    this.templateService.createTemplate(payload).subscribe({
      next: (t) => {
        this.templates = sortTemplates([...this.templates, t]);
        this.toggleForm();
        this.notifications.success('Plantilla creada');
      },
      error: () => this.notifications.error('Error al crear plantilla'),
    });
  }

  deleteTemplate(id: string): void {
    if (!confirm('¿Eliminar plantilla?')) return;
    this.templateService.deleteTemplate(id).subscribe({
      next: () => {
        this.templates = this.templates.filter((t) => t.id !== id);
        this.notifications.success('Plantilla eliminada');
      },
      error: () => this.notifications.error('No se pudo eliminar'),
    });
  }
}
