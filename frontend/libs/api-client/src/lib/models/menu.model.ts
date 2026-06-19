export interface Menu {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  is_published: boolean;
  display_order: number;
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
  created_at: string;
  updated_at: string;
}

export interface CreateMenuRequest {
  name: string;
  description?: string;
}

export interface UpdateMenuRequest {
  name?: string;
  description?: string;
  is_published?: boolean;
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
}

export interface UpdateMenuItemRequest {
  name?: string;
  description?: string;
  price_amount?: string;
  price_currency?: string;
  is_available?: boolean;
  display_order?: number;
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
