import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { SettingsService, UserSettings } from '../../services/settings.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="settings-container">
      <header class="header">
        <h1>Account Settings</h1>
        <p>Manage your AI credentials and model preferences for personalized generation.</p>
      </header>

      <div class="settings-grid">
        <!-- API Credentials -->
        <div class="card">
          <div class="card-header">
            <div class="icon">🔑</div>
            <div>
              <h3>AI Credentials</h3>
              <p>Your keys are used to bypass global rate limits.</p>
            </div>
          </div>
          
          <form [formGroup]="settingsForm" class="settings-form">
            <div class="field">
              <label>Google Gemini API Key</label>
              <input type="password" formControlName="gemini_api_key" placeholder="AIzaSy...">
              <small>Used for script generation. Get it at Google AI Studio.</small>
            </div>

            <div class="field">
              <label>OpenAI API Key</label>
              <input type="password" formControlName="openai_api_key" placeholder="sk-...">
              <small>Used for DALL-E 3 and high-quality TTS.</small>
            </div>
          </form>
        </div>

        <!-- Model Preferences -->
        <div class="card">
          <div class="card-header">
            <div class="icon">🤖</div>
            <div>
              <h3>Model Preferences</h3>
              <p>Configure which engines power your studio.</p>
            </div>
          </div>

          <form [formGroup]="settingsForm" class="settings-form">
            <div class="field">
              <label>Scripting Model (Gemini)</label>
              <select formControlName="preferred_gemini_model">
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fastest)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Most Creative)</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash (Next Gen)</option>
              </select>
            </div>

            <div class="field">
              <label>Image Engine</label>
              <select formControlName="preferred_image_model">
                <option value="dall-e-3">DALL-E 3 (Highest Quality)</option>
                <option value="stable-diffusion-xl">Stable Diffusion XL (Fast)</option>
              </select>
            </div>
          </form>
        </div>
      </div>

      <div class="actions">
        <button (click)="saveSettings()" class="btn-primary" [disabled]="loading">
          <span *ngIf="!loading">Save Changes</span>
          <span *ngIf="loading">Saving...</span>
        </button>
        <p *ngIf="successMsg" class="success-msg">{{ successMsg }}</p>
      </div>
    </div>
  `,
  styles: [`
    .settings-container { max-width: 900px; margin: 0 auto; animation: fadeUp 0.3s ease-out; }
    .header { margin-bottom: 32px; }
    .header h1 { font-size: 1.5rem; font-weight: 800; margin: 0; }
    .header p { color: var(--text-muted); margin-top: 4px; }

    .settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; box-shadow: var(--shadow-sm); }
    .card-header { display: flex; gap: 16px; align-items: flex-start; margin-bottom: 24px; }
    .card-header .icon { width: 40px; height: 40px; background: var(--bg-body); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
    .card-header h3 { margin: 0; font-size: 1rem; font-weight: 700; }
    .card-header p { margin: 2px 0 0; font-size: 0.75rem; color: var(--text-muted); }

    .field { margin-bottom: 20px; }
    .field label { display: block; font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 6px; text-transform: uppercase; }
    .field input, .field select { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.875rem; transition: all 0.2s; }
    .field input:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
    .field small { display: block; margin-top: 6px; font-size: 0.7rem; color: var(--text-muted); }

    .actions { display: flex; align-items: center; gap: 16px; border-top: 1px solid var(--border); pt: 24px; }
    .btn-primary { background: var(--primary); color: white; border: none; padding: 12px 32px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
    .btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
    .success-msg { color: #059669; font-size: 0.875rem; font-weight: 600; }

    @media (max-width: 768px) { .settings-grid { grid-template-columns: 1fr; } }
  `]
})
export class SettingsComponent implements OnInit {
  settingsForm: FormGroup;
  loading = false;
  successMsg = '';

  constructor(private fb: FormBuilder, private settingsService: SettingsService) {
    this.settingsForm = this.fb.group({
      gemini_api_key: [''],
      openai_api_key: [''],
      preferred_gemini_model: ['gemini-1.5-flash'],
      preferred_image_model: ['dall-e-3']
    });
  }

  ngOnInit() {
    this.settingsService.getSettings().subscribe(s => {
      this.settingsForm.patchValue(s);
    });
  }

  saveSettings() {
    this.loading = true;
    this.successMsg = '';
    this.settingsService.updateSettings(this.settingsForm.value).subscribe({
      next: () => {
        this.loading = false;
        this.successMsg = 'Settings saved successfully!';
        setTimeout(() => this.successMsg = '', 3000);
      },
      error: () => {
        this.loading = false;
        alert('Error saving settings');
      }
    });
  }
}
