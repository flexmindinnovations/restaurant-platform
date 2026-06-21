import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { User, UserListParams, UserRole } from './users.model';

const MOCK_USERS: User[] = [
  {
    id: 'u1',
    email: 'admin@quickbite.com',
    phone_number: '+15550100',
    first_name: 'Sarah',
    last_name: 'Connor',
    display_name: 'Sarah Connor',
    roles: ['SUPER_ADMIN'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
    created_at: '2025-01-15T08:00:00Z',
  },
  {
    id: 'u2',
    email: 'john.doe@gmail.com',
    phone_number: '+15550101',
    first_name: 'John',
    last_name: 'Doe',
    display_name: 'John Doe',
    roles: ['CUSTOMER'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150',
    created_at: '2026-02-10T12:30:00Z',
  },
  {
    id: 'u3',
    email: 'partner.delivery@quickbite.com',
    phone_number: '+15550102',
    first_name: 'Marcus',
    last_name: 'Vance',
    display_name: 'Marcus Vance',
    roles: ['DELIVERY_PARTNER'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150',
    created_at: '2026-03-20T14:15:00Z',
  },
  {
    id: 'u4',
    email: 'owner.pizza@gmail.com',
    phone_number: '+15550103',
    first_name: 'Luigi',
    last_name: 'Mario',
    display_name: 'Luigi Pizza',
    roles: ['RESTAURANT_OWNER'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150',
    created_at: '2026-04-01T09:45:00Z',
  },
  {
    id: 'u5',
    email: 'jane.smith@yahoo.com',
    phone_number: '+15550104',
    first_name: 'Jane',
    last_name: 'Smith',
    display_name: 'Jane Smith',
    roles: ['CUSTOMER'],
    is_active: false,
    avatar_url: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150',
    created_at: '2026-04-18T16:22:00Z',
  },
  {
    id: 'u6',
    email: 'bob.builder@gmail.com',
    phone_number: '+15550105',
    first_name: 'Robert',
    last_name: 'Builder',
    display_name: 'Bob Builder',
    roles: ['DELIVERY_PARTNER'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
    created_at: '2026-05-05T11:00:00Z',
  },
  {
    id: 'u7',
    email: 'owner.burger@outlook.com',
    phone_number: '+15550106',
    first_name: 'Gordon',
    last_name: 'Ramsay',
    display_name: 'Gordon Burger',
    roles: ['RESTAURANT_OWNER'],
    is_active: true,
    avatar_url: 'https://images.unsplash.com/photo-1556157382-97eda2d62296?w=150',
    created_at: '2026-05-20T10:10:00Z',
  },
];

@Injectable({ providedIn: 'root' })
export class UsersService {
  private users: User[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('quickbite_users');
      if (stored) {
        try {
          this.users = JSON.parse(stored);
        } catch {
          this.users = [...MOCK_USERS];
        }
      } else {
        this.users = [...MOCK_USERS];
        localStorage.setItem('quickbite_users', JSON.stringify(this.users));
      }
    } else {
      this.users = [...MOCK_USERS];
    }
  }

  private save(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_users', JSON.stringify(this.users));
    }
  }

  list(params?: UserListParams): Observable<{ items: User[]; total: number }> {
    let filtered = [...this.users];

    if (params?.search) {
      const q = params.search.toLowerCase();
      filtered = filtered.filter(
        (u) =>
          u.display_name.toLowerCase().includes(q) ||
          u.email.toLowerCase().includes(q) ||
          u.phone_number.includes(q),
      );
    }

    if (params?.role && params.role !== 'ALL') {
      filtered = filtered.filter((u) => u.roles.includes(params.role as UserRole));
    }

    if (params?.is_active !== undefined) {
      filtered = filtered.filter((u) => u.is_active === params.is_active);
    }

    const total = filtered.length;
    const skip = params?.skip ?? 0;
    const limit = params?.limit ?? 10;
    const items = filtered.slice(skip, skip + limit);

    return of({ items, total }).pipe(delay(200));
  }

  updateRole(id: string, roles: UserRole[]): Observable<User> {
    const user = this.users.find((u) => u.id === id);
    if (!user) {
      throw new Error('User not found');
    }
    user.roles = roles;
    this.save();
    return of({ ...user }).pipe(delay(150));
  }

  toggleStatus(id: string): Observable<User> {
    const user = this.users.find((u) => u.id === id);
    if (!user) {
      throw new Error('User not found');
    }
    user.is_active = !user.is_active;
    this.save();
    return of({ ...user }).pipe(delay(150));
  }
}
