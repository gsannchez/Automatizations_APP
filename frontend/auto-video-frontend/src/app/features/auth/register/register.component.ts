import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <h1>Create Account</h1>
        <p class="subtitle">Join Auto Video Maker today</p>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input id="email" type="email" formControlName="email" placeholder="name@company.com">
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input id="password" type="password" formControlName="password" placeholder="••••••••">
          </div>

          <button type="submit" [disabled]="registerForm.invalid || loading">
            {{ loading ? 'Creating Account...' : 'Continue' }}
          </button>
        </form>

        <div class="footer">
          Already have an account? <a routerLink="/login">Sign in</a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      padding: 1rem;
    }
    .auth-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 1.5rem;
      padding: 2.5rem;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    h1 { color: white; font-size: 1.875rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; }
    .subtitle { color: #94a3b8; text-align: center; margin-bottom: 2rem; }
    .form-group { margin-bottom: 1.5rem; }
    label { display: block; color: #cbd5e1; font-size: 0.875rem; margin-bottom: 0.5rem; }
    input {
      width: 100%;
      background: rgba(0,0,0,0.2);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 0.75rem;
      padding: 0.75rem 1rem;
      color: white;
      transition: all 0.2s;
    }
    input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2); }
    button {
      width: 100%;
      background: #6366f1;
      color: white;
      border: none;
      border-radius: 0.75rem;
      padding: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      margin-top: 1rem;
    }
    button:hover:not(:disabled) { background: #4f46e5; transform: translateY(-1px); }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .footer { text-align: center; margin-top: 1.5rem; color: #94a3b8; font-size: 0.875rem; }
    a { color: #818cf8; text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; }
  `]
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  registerForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });
  
  loading = false;

  onSubmit() {
    if (this.registerForm.valid) {
      this.loading = true;
      const { email, password } = this.registerForm.value;
      this.authService.register(email!, password!).subscribe({
        next: () => this.router.navigate(['/dashboard']),
        error: (err) => {
          this.loading = false;
          alert('Registration failed: ' + (err.error?.detail || err.message));
        }
      });
    }
  }
}
