import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ChannelService, Channel } from '../../../services/channel.service';

@Component({
  selector: 'app-channel-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="container">
      <header class="header">
        <div class="header-text">
          <h1>Social Channels</h1>
          <p>Link your social accounts to automate your video publishing workflow.</p>
        </div>
        <button (click)="toggleForm()" class="btn-primary">
          {{ showForm ? 'Close' : '+ Connect New' }}
        </button>
      </header>

      <div class="form-overlay" *ngIf="showForm" (click)="toggleForm()">
        <div class="modal-card" (click)="$event.stopPropagation()">
          <h3>Connect Channel</h3>
          <p>Select platform and provide a friendly name.</p>
          <form [formGroup]="channelForm" (ngSubmit)="onSubmit()">
            <div class="field">
              <label>Friendly Name</label>
              <input type="text" formControlName="name" placeholder="e.g. My Tech Shorts">
            </div>
            <div class="field">
              <label>Platform</label>
              <div class="platform-selector">
                <label class="p-option" [class.selected]="channelForm.get('platform')?.value === 'youtube'">
                  <input type="radio" formControlName="platform" value="youtube">
                  <span>YouTube</span>
                </label>
                <label class="p-option" [class.selected]="channelForm.get('platform')?.value === 'tiktok'">
                  <input type="radio" formControlName="platform" value="tiktok">
                  <span>TikTok</span>
                </label>
                <label class="p-option" [class.selected]="channelForm.get('platform')?.value === 'instagram'">
                  <input type="radio" formControlName="platform" value="instagram">
                  <span>Instagram</span>
                </label>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-ghost" (click)="toggleForm()">Cancel</button>
              <button type="submit" class="btn-primary" [disabled]="channelForm.invalid">Connect Channel</button>
            </div>
          </form>
        </div>
      </div>

      <div class="channels-grid">
        <div class="channel-card" *ngFor="let channel of channels">
          <div class="card-top">
            <div class="platform-icon" [ngClass]="channel.platform">
              <span *ngIf="channel.platform === 'youtube'">▶</span>
              <span *ngIf="channel.platform === 'tiktok'">♪</span>
              <span *ngIf="channel.platform === 'instagram'">📸</span>
            </div>
            <button class="btn-delete" (click)="deleteChannel(channel.id)" title="Remove channel">×</button>
          </div>
          <div class="card-body">
            <h4>{{ channel.name }}</h4>
            <div class="platform-badge">{{ channel.platform }}</div>
          </div>
          <div class="card-footer">
            <span class="status-dot"></span> Active & Linked
          </div>
        </div>

        <div *ngIf="channels.length === 0 && !showForm" class="empty-state">
          <div class="empty-art">📺</div>
          <h3>No channels linked yet</h3>
          <p>Connect your first channel to start publishing your AI videos automatically.</p>
          <button (click)="toggleForm()" class="btn-primary mt-4">Get Started</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .container { max-width: 1000px; margin: 0 auto; animation: fadeUp 0.3s ease-out; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
    .header h1 { font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
    .header p { color: var(--text-muted); margin: 6px 0 0; font-size: 0.875rem; }

    /* Modal Form */
    .form-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.2s ease-out; }
    .modal-card { background: var(--bg-card); border-radius: 16px; padding: 32px; width: 100%; max-width: 450px; box-shadow: var(--shadow-lg); animation: fadeUp 0.3s ease-out; }
    .modal-card h3 { margin: 0 0 8px; font-size: 1.25rem; font-weight: 700; }
    .modal-card p { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 24px; }
    .modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }

    .platform-selector { display: flex; gap: 10px; margin-top: 8px; }
    .p-option { flex: 1; border: 1px solid var(--border); padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .p-option input { display: none; }
    .p-option span { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); }
    .p-option:hover { border-color: var(--primary); background: var(--bg-body); }
    .p-option.selected { border-color: var(--primary); background: var(--primary-light); }
    .p-option.selected span { color: var(--primary); }

    /* Grid */
    .channels-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }

    .channel-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; transition: all 0.2s; box-shadow: var(--shadow-xs); }
    .channel-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); border-color: var(--primary); }

    .card-top { padding: 16px; display: flex; justify-content: space-between; align-items: flex-start; }
    .platform-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: white; }
    .platform-icon.youtube { background: #ef4444; }
    .platform-icon.tiktok { background: #000000; }
    .platform-icon.instagram { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }

    .btn-delete { background: none; border: none; font-size: 1.25rem; color: var(--text-muted); cursor: pointer; line-height: 1; padding: 4px; }
    .btn-delete:hover { color: var(--danger); }

    .card-body { padding: 0 16px 16px; }
    .card-body h4 { margin: 0 0 4px; font-size: 1rem; font-weight: 700; }
    .platform-badge { display: inline-block; padding: 2px 8px; background: var(--bg-body); border-radius: 4px; font-size: 0.6875rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

    .card-footer { padding: 12px 16px; background: var(--bg-hover); border-top: 1px solid var(--border); font-size: 0.75rem; font-weight: 500; color: var(--success); display: flex; align-items: center; gap: 6px; }
    .status-dot { width: 6px; height: 6px; background: var(--success); border-radius: 50%; display: block; }

    /* Empty State */
    .empty-state { grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: var(--bg-card); border: 2px dashed var(--border); border-radius: 16px; }
    .empty-art { font-size: 3rem; margin-bottom: 16px; opacity: 0.3; }
    .empty-state h3 { font-size: 1.25rem; font-weight: 700; margin: 0 0 8px; }
    .empty-state p { color: var(--text-muted); font-size: 0.9375rem; max-width: 400px; margin: 0 auto; }

    .mt-4 { margin-top: 24px; }
    .btn-primary { background: var(--primary); color: white; padding: 10px 20px; border-radius: 8px; font-weight: 700; border: none; cursor: pointer; transition: all 0.2s; }
    .btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
    .btn-ghost { background: transparent; color: var(--text-secondary); padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-ghost:hover { background: var(--bg-body); }
  `]
})
export class ChannelListComponent implements OnInit {
  channels: Channel[] = [];
  showForm = false;
  channelForm: FormGroup;

  constructor(private channelService: ChannelService, private fb: FormBuilder) {
    this.channelForm = this.fb.group({
      name: ['', Validators.required],
      platform: ['youtube', Validators.required]
    });
  }

  ngOnInit() { this.loadChannels(); }

  loadChannels() {
    this.channelService.getChannels().subscribe(data => this.channels = data);
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) this.channelForm.reset({ platform: 'youtube' });
  }

  onSubmit() {
    if (this.channelForm.valid) {
      this.channelService.createChannel(this.channelForm.value).subscribe(channel => {
        this.channels.push(channel);
        this.toggleForm();
      });
    }
  }

  deleteChannel(id: number) {
    if (confirm('Disconnect this channel?')) {
      this.channelService.deleteChannel(id).subscribe(() => {
        this.channels = this.channels.filter(c => c.id !== id);
      });
    }
  }
}
