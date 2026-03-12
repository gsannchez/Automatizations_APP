import { HttpClient } from '@angular/common/http';
import { Observable, tap, of } from 'rxjs';
import { Router } from '@angular/router';
import { PLATFORM_ID, Inject, Injectable, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  plan: string;
  minutes_used: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = '/api/v1/auth';
  
  // Reactive state for the current user
  currentUser = signal<UserProfile | null>(null);

  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Try to load user if token exists (browser only)
    if (isPlatformBrowser(this.platformId) && this.isLoggedIn()) {
      this.fetchMe().subscribe();
    }
  }

  register(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API_URL}/register`, { email, password }).pipe(
      tap(res => this.handleAuthSuccess(res))
    );
  }

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API_URL}/login`, { email, password }).pipe(
      tap(res => this.handleAuthSuccess(res))
    );
  }

  refresh(): Observable<{ access_token: string }> {
    if (!isPlatformBrowser(this.platformId)) return of({ access_token: '' });
    
    const refresh_token = localStorage.getItem('refresh_token');
    return this.http.post<{ access_token: string }>(`${this.API_URL}/refresh`, { refresh_token }).pipe(
      tap(res => localStorage.setItem('access_token', res.access_token))
    );
  }

  fetchMe(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.API_URL}/me`).pipe(
      tap(user => this.currentUser.set(user))
    );
  }

  logout() {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      return !!localStorage.getItem('access_token');
    }
    return false;
  }

  private handleAuthSuccess(res: TokenResponse) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);
    }
    this.fetchMe().subscribe();
  }
}
