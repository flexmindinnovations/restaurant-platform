export interface Review {
  id: string;
  restaurant_id: string;
  restaurant_name: string;
  customer_name: string;
  rating: number;
  comment: string;
  created_at: string;
  flagged: boolean;
  status: 'APPROVED' | 'PENDING' | 'FLAGGED' | 'REJECTED';
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE';
  tags: string[];
  owner_reply: string | null;
}
