export type PartnerStatus = 'ONLINE' | 'BUSY' | 'OFFLINE';

export interface Coordinates {
  lat: number;
  lng: number;
  label?: string;
}

export interface DeliveryPartner {
  id: string;
  name: string;
  phone: string;
  status: PartnerStatus;
  vehicle_type: 'BICYCLE' | 'SCOOTER' | 'CAR';
  current_location: Coordinates;
}

export interface ActiveDelivery {
  id: string; // matches orderId
  restaurant_name: string;
  restaurant_location: Coordinates;
  customer_address: string;
  customer_location: Coordinates;
  partner_id: string | null;
  partner_name: string | null;
  status: 'PENDING' | 'ASSIGNED' | 'PICKED_UP' | 'DELIVERED';
}
