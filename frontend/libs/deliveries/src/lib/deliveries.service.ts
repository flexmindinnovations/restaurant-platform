import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { DeliveryPartner, ActiveDelivery } from './deliveries.model';

const MOCK_PARTNERS: DeliveryPartner[] = [
  {
    id: 'dp1',
    name: 'Alex Rivera',
    phone: '+15550201',
    status: 'ONLINE',
    vehicle_type: 'SCOOTER',
    current_location: { lat: 37.7749, lng: -122.4194, label: 'Downtown' },
  },
  {
    id: 'dp2',
    name: 'Chloe Bennett',
    phone: '+15550202',
    status: 'BUSY',
    vehicle_type: 'CAR',
    current_location: { lat: 37.7833, lng: -122.4167, label: 'Financial District' },
  },
  {
    id: 'dp3',
    name: 'David Kim',
    phone: '+15550203',
    status: 'ONLINE',
    vehicle_type: 'BICYCLE',
    current_location: { lat: 37.7699, lng: -122.4468, label: 'Haight-Ashbury' },
  },
  {
    id: 'dp4',
    name: 'Elena Rostova',
    phone: '+15550204',
    status: 'OFFLINE',
    vehicle_type: 'CAR',
    current_location: { lat: 37.7599, lng: -122.4376, label: 'Noe Valley' },
  },
  {
    id: 'dp5',
    name: 'Marcus Vance',
    phone: '+15550102',
    status: 'ONLINE',
    vehicle_type: 'BICYCLE',
    current_location: { lat: 37.7891, lng: -122.4014, label: 'SOMA' },
  },
];

const MOCK_DELIVERIES: ActiveDelivery[] = [
  {
    id: 'ord-101',
    restaurant_name: 'Pizza Roma',
    restaurant_location: { lat: 37.778, lng: -122.412 },
    customer_address: '852 Folsom St, San Francisco, CA',
    customer_location: { lat: 37.781, lng: -122.404 },
    partner_id: 'dp2',
    partner_name: 'Chloe Bennett',
    status: 'PICKED_UP',
  },
  {
    id: 'ord-102',
    restaurant_name: 'Burger Joint',
    restaurant_location: { lat: 37.765, lng: -122.44 },
    customer_address: '1240 Castro St, San Francisco, CA',
    customer_location: { lat: 37.752, lng: -122.435 },
    partner_id: null,
    partner_name: null,
    status: 'PENDING',
  },
  {
    id: 'ord-103',
    restaurant_name: 'Sushi Zen',
    restaurant_location: { lat: 37.789, lng: -122.42 },
    customer_address: '2200 Broadway, San Francisco, CA',
    customer_location: { lat: 37.795, lng: -122.432 },
    partner_id: null,
    partner_name: null,
    status: 'PENDING',
  },
];

@Injectable({ providedIn: 'root' })
export class DeliveriesService {
  private partners: DeliveryPartner[] = [];
  private deliveries: ActiveDelivery[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      const storedP = localStorage.getItem('quickbite_partners');
      const storedD = localStorage.getItem('quickbite_deliveries');
      if (storedP && storedD) {
        try {
          this.partners = JSON.parse(storedP);
          this.deliveries = JSON.parse(storedD);
        } catch {
          this.resetMocks();
        }
      } else {
        this.resetMocks();
      }
    } else {
      this.partners = [...MOCK_PARTNERS];
      this.deliveries = [...MOCK_DELIVERIES];
    }
  }

  private resetMocks(): void {
    this.partners = [...MOCK_PARTNERS];
    this.deliveries = [...MOCK_DELIVERIES];
    this.save();
  }

  private save(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_partners', JSON.stringify(this.partners));
      localStorage.setItem('quickbite_deliveries', JSON.stringify(this.deliveries));
    }
  }

  getPartners(): Observable<DeliveryPartner[]> {
    return of([...this.partners]).pipe(delay(200));
  }

  getActiveDeliveries(): Observable<ActiveDelivery[]> {
    return of([...this.deliveries]).pipe(delay(200));
  }

  overrideAssignment(
    deliveryId: string,
    partnerId: string | null,
  ): Observable<{ partners: DeliveryPartner[]; deliveries: ActiveDelivery[] }> {
    const delivery = this.deliveries.find((d) => d.id === deliveryId);
    if (!delivery) throw new Error('Delivery not found');

    const oldPartnerId = delivery.partner_id;

    if (partnerId === null) {
      // Unassign
      delivery.partner_id = null;
      delivery.partner_name = null;
      delivery.status = 'PENDING';

      if (oldPartnerId) {
        const oldP = this.partners.find((p) => p.id === oldPartnerId);
        if (oldP) oldP.status = 'ONLINE';
      }
    } else {
      const partner = this.partners.find((p) => p.id === partnerId);
      if (!partner) throw new Error('Partner not found');

      // Free previous partner if any
      if (oldPartnerId) {
        const oldP = this.partners.find((p) => p.id === oldPartnerId);
        if (oldP) oldP.status = 'ONLINE';
      }

      delivery.partner_id = partner.id;
      delivery.partner_name = partner.name;
      delivery.status = 'ASSIGNED';
      partner.status = 'BUSY';
    }

    this.save();
    return of({ partners: [...this.partners], deliveries: [...this.deliveries] }).pipe(delay(200));
  }
}
