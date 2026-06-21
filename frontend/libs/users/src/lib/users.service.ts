import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { User, UserListParams, UserRole, UserProfile } from './users.model';

@Injectable({ providedIn: 'root' })
export class UsersService {
  private readonly http = inject(HttpClient);

  list(params?: UserListParams): Observable<{ items: User[]; total: number }> {
    let httpParams = new HttpParams();
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    if (params?.role && params.role !== 'ALL') httpParams = httpParams.set('role', params.role);
    if (params?.is_active !== undefined) httpParams = httpParams.set('is_active', params.is_active);

    return this.http
      .get<{ data: { items: User[]; total: number } }>('/api/v1/admin/users', { params: httpParams })
      .pipe(map((res) => res.data || { items: [], total: 0 }));
  }

  updateRole(id: string, roles: UserRole[]): Observable<User> {
    return this.http
      .patch<{ data: any }>(`/api/v1/admin/users/${id}/role`, { roles })
      .pipe(
        map(() => ({
          id,
          email: '',
          phone_number: '',
          first_name: '',
          last_name: '',
          display_name: '',
          roles,
          is_active: true,
          created_at: '',
        }))
      );
  }

  toggleStatus(id: string): Observable<User> {
    return this.http
      .post<{ data: any }>(`/api/v1/admin/users/${id}/toggle-status`, {})
      .pipe(
        map(() => ({
          id,
          email: '',
          phone_number: '',
          first_name: '',
          last_name: '',
          display_name: '',
          roles: [],
          is_active: false,
          created_at: '',
        }))
      );
  }

  getProfile(): Observable<UserProfile> {
    return this.http
      .get<{ data: UserProfile }>('/api/v1/me')
      .pipe(map((res) => res.data));
  }

  updateProfile(profile: Partial<UserProfile>): Observable<{ message: string }> {
    return this.http
      .patch<{ data: { message: string } }>('/api/v1/me', profile)
      .pipe(map((res) => res.data));
  }
}
