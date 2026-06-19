export type PaymentStatus = 'SUCCESS' | 'REFUNDED' | 'FAILED';

export interface PaymentTransaction {
  id: string;
  order_id: string;
  customer_name: string;
  amount: number;
  status: PaymentStatus;
  payment_method: string;
  created_at: string;
}

export interface PaymentListParams {
  skip?: number;
  limit?: number;
  search?: string;
  status?: PaymentStatus | 'ALL';
}
