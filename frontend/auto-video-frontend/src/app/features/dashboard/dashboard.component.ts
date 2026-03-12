import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoListComponent } from '../videos/video-list/video-list.component';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, VideoListComponent],
  templateUrl: './dashboard.component.html',
  styles: [`
    .dashboard-container { padding: 2rem; max-width: 1200px; margin: 0 auto; }
    .welcome-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    .welcome-header h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0; }
    .subtitle { color: #94a3b8; margin: 0.5rem 0 0 0; }
    .user-info { display: flex; align-items: center; gap: 1rem; }
    .plan-badge { background: rgba(99, 102, 241, 0.1); color: #818cf8; padding: 0.4rem 1rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(129, 140, 248, 0.2); }
    .btn-logout { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.2); padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; transition: all 0.2s; }
    .btn-logout:hover { background: rgba(239, 68, 68, 0.2); }
    
    .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
    .stat-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1rem; padding: 1.5rem; }
    .stat-card label { display: block; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .stat-card .value { color: white; font-size: 1.5rem; font-weight: 700; }
    .stat-card .status { font-size: 0.75rem; margin-top: 0.5rem; color: #4ade80; }
    
    .content-section { animation: fadeIn 0.5s ease-out; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class DashboardComponent implements OnInit {
  user: any;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.authService.fetchMe().subscribe(user => {
      this.user = user;
    });
  }

  logout() {
    this.authService.logout();
    window.location.reload();
  }
}
