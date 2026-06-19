export interface PlatformSettings {
  commission_rate: number;
  delivery_radius_km: number;
  min_order_value: number;
  base_delivery_fee: number;
  service_fee: number;
  ai_provider: 'Gemini' | 'OpenAI';
  ai_api_key: string;
}

