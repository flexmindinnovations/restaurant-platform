export interface Restaurant {
  id: string;
  owner_id: string;
  name: string;
  phone: string;
  email: string;
  address_street: string;
  address_city: string;
  address_state: string;
  address_postal_code: string;
  address_country: string;
  address_latitude: number | null;
  address_longitude: number | null;
  cuisine_types: string[];
  description: string | null;
  operating_hours: Record<string, { open: string; close: string }>;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateRestaurantRequest {
  name: string;
  phone: string;
  email: string;
  address_street: string;
  address_city: string;
  address_state: string;
  address_postal_code: string;
  address_country: string;
  address_latitude?: number;
  address_longitude?: number;
  cuisine_types: string[];
  description?: string;
  operating_hours: Record<string, { open: string; close: string }>;
}

export interface UpdateRestaurantRequest {
  name?: string;
  phone?: string;
  email?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_postal_code?: string;
  address_country?: string;
  description?: string;
  operating_hours?: Record<string, { open: string; close: string }>;
}

export interface RestaurantListParams {
  skip?: number;
  limit?: number;
  search?: string;
  is_verified?: boolean;
}

export interface PaginatedResponse<T> {
  data: {
    items: T[];
    total: number;
  };
}

export interface ApiResponse<T> {
  data: T;
}
