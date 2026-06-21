export interface Menu {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  categories: Category[];
}

export interface Category {
  id: string;
  menu_id: string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  items: MenuItem[];
}

export interface MenuItem {
  id: string;
  menu_id: string;
  category_id: string | null;
  name: string;
  description: string | null;
  price_amount: string;
  price_currency: string;
  is_available: boolean;
  display_order: number;
  image_url: string | null;
  dietary_labels?: string[];
  preparation_time_minutes?: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateMenuRequest {
  name: string;
  description?: string;
  restaurant_id?: string;
}

export interface UpdateMenuRequest {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface CreateCategoryRequest {
  name: string;
  description?: string;
  display_order?: number;
}

export interface UpdateCategoryRequest {
  name?: string;
  description?: string;
  display_order?: number;
}

export interface CreateMenuItemRequest {
  name: string;
  description?: string;
  price_amount: string;
  price_currency: string;
  category_id?: string;
  display_order?: number;
  image_url?: string | null;
  dietary_labels?: string[];
  preparation_time_minutes?: number | null;
}

export interface UpdateMenuItemRequest {
  name?: string;
  description?: string;
  price_amount?: string;
  price_currency?: string;
  is_available?: boolean;
  display_order?: number;
  category_id?: string;
  image_url?: string | null;
  dietary_labels?: string[];
  preparation_time_minutes?: number | null;
}

export interface MenuListParams {
  restaurant_id?: string;
  skip?: number;
  limit?: number;
}

export interface MenuSearchResult {
  items: MenuItem[];
  total: number;
}
