import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService } from '../../../services/video.service';
import { interval, Subscription, switchMap, startWith } from 'rxjs';

@Component({
  selector: 'app-video-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="video-list-container">
      <div class="header">
        <h2>My Videos</h2>
        <div class="pagination-controls">
          <button (click)="prevPage()" [disabled]="page === 1">Previous</button>
          <span>Page {{ page }} of {{ totalPages }}</span>
          <button (click)="nextPage()" [disabled]="page >= totalPages">Next</button>
        </div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Progress</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let video of videos">
              <td>{{ video.title }}</td>
              <td>
                <span class="status-badge" [ngClass]="video.status.toLowerCase()">
                  {{ video.status }}
                </span>
              </td>
              <td>
                <div class="progress-bar-container">
                  <div class="progress-bar" [style.width.%]="video.progress"></div>
                  <span>{{ video.progress }}%</span>
                </div>
              </td>
              <td>{{ video.created_at | date:'short' }}</td>
              <td>
                <button *ngIf="video.status === 'DONE'" (click)="downloadVideo(video.id)" class="download-btn">
                  Download
                </button>
                <span *ngIf="video.status === 'FAILED'" class="error-text">Failed</span>
                <span *ngIf="['QUEUED', 'PROCESSING'].includes(video.status) || !['DONE', 'FAILED'].includes(video.status)" class="polling-text">
                  Processing...
                </span>
              </td>
            </tr>
            <tr *ngIf="videos.length === 0">
              <td colspan="5" class="empty-state">No videos found. Create your first one!</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .video-list-container { background: rgba(255, 255, 255, 0.05); border-radius: 1rem; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1); }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
    h2 { color: white; margin: 0; }
    
    .pagination-controls { display: flex; align-items: center; gap: 1rem; color: #94a3b8; font-size: 0.875rem; }
    .pagination-controls button { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.1); color: white; padding: 0.4rem 0.8rem; border-radius: 0.5rem; cursor: pointer; }
    .pagination-controls button:disabled { opacity: 0.3; cursor: not-allowed; }
    
    .table-container { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; padding: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
    td { padding: 1rem; color: #cbd5e1; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
    
    .status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .status-badge.done { background: rgba(34, 197, 94, 0.1); color: #4ade80; }
    .status-badge.failed { background: rgba(239, 68, 68, 0.1); color: #f87171; }
    .status-badge.queued, .status-badge.processing { background: rgba(234, 179, 8, 0.1); color: #facc15; }
    
    .progress-bar-container { display: flex; align-items: center; gap: 0.5rem; width: 120px; }
    .progress-bar { height: 4px; background: #6366f1; border-radius: 2px; }
    .progress-bar-container span { font-size: 0.75rem; color: #94a3b8; }
    
    .download-btn { background: #6366f1; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.75rem; }
    .error-text { color: #f87171; font-size: 0.75rem; }
    .polling-text { color: #94a3b8; font-size: 0.75rem; font-style: italic; }
    .empty-state { text-align: center; color: #64748b; padding: 3rem; }
  `]
})
export class VideoListComponent implements OnInit, OnDestroy {
  videos: any[] = [];
  page = 1;
  limit = 10;
  total = 0;
  private pollingSub?: Subscription;

  constructor(private videoService: VideoService) {}

  ngOnInit() {
    this.loadVideos();
    // Start polling every 5 seconds for status updates
    this.pollingSub = interval(5000).subscribe(() => this.updateVideoStatuses());
  }

  ngOnDestroy() {
    if (this.pollingSub) {
      this.pollingSub.unsubscribe();
    }
  }

  loadVideos() {
    this.videoService.listVideos(this.page, this.limit).subscribe(response => {
      this.videos = response.items;
      this.total = response.total;
    });
  }

  updateVideoStatuses() {
    // Only poll videos that are not in terminal state
    const activeVideos = this.videos.filter(v => !['DONE', 'FAILED'].includes(v.status));
    
    activeVideos.forEach(v => {
      this.videoService.getVideoStatus(v.id).subscribe(statusUpdate => {
        v.status = statusUpdate.status;
        v.progress = statusUpdate.progress;
      });
    });
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit) || 1;
  }

  nextPage() {
    if (this.page < this.totalPages) {
      this.page++;
      this.loadVideos();
    }
  }

  prevPage() {
    if (this.page > 1) {
      this.page--;
      this.loadVideos();
    }
  }

  downloadVideo(videoId: string) {
    this.videoService.getDownloadUrl(videoId).subscribe(response => {
      window.open(response.download_url, '_blank');
    });
  }
}
