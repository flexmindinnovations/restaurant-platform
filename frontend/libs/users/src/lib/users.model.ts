export type UserRole = 'CUSTOMER' | 'DELIVERY_PARTNER' | 'RESTAURANT_OWNER' | 'SUPER_ADMIN';

export interface User {
  id: string;
  email: string;
  phone_number: string;
  first_name: string;
  last_name: string;
  display_name: string;
  roles: UserRole[];
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface UserListParams {
  skip?: number;
  limit?: number;
  search?: string;
  role?: UserRole | 'ALL';
  is_active?: boolean;
}

export interface UserProfile {
  id: string;
  account_id: string;
  first_name: string | null;
  last_name: string | null;
  display_name: string | null;
  avatar_url: string | null;
  preferred_language: string | null;
  created_at?: string;
  updated_at?: string;
}
