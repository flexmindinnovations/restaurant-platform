import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { Review } from './reviews.model';

const MOCK_REVIEWS: Review[] = [
  {
    id: 'rev-1',
    restaurant_id: 'rest-1',
    restaurant_name: 'Golden Dragon',
    customer_name: 'John Doe',
    rating: 5,
    comment: 'The Peking Duck was absolutely spectacular! Service was super fast and friendly.',
    created_at: '2026-06-18T14:32:00Z',
    flagged: false,
    status: 'APPROVED',
    sentiment: 'POSITIVE',
    tags: ['Spectacular Peking Duck', 'Fast Service', 'Friendly Staff'],
    owner_reply: 'Thank you John! We hope to serve you again soon!',
  },
  {
    id: 'rev-2',
    restaurant_id: 'rest-2',
    restaurant_name: 'Pizza Suprema',
    customer_name: 'Jane Smith',
    rating: 2,
    comment:
      'Pizza was extremely cold when it arrived. The crust was soggy and toppings were sparse.',
    created_at: '2026-06-18T18:15:00Z',
    flagged: true,
    status: 'FLAGGED',
    sentiment: 'NEGATIVE',
    tags: ['Cold Pizza', 'Soggy Crust', 'Sparse Toppings'],
    owner_reply: null,
  },
  {
    id: 'rev-3',
    restaurant_id: 'rest-3',
    restaurant_name: 'Burger Palace',
    customer_name: 'Mike Johnson',
    rating: 4,
    comment:
      'Great double cheeseburger! Onion rings could have been crispier, but overall very good.',
    created_at: '2026-06-17T12:00:00Z',
    flagged: false,
    status: 'APPROVED',
    sentiment: 'POSITIVE',
    tags: ['Great Double Cheeseburger', 'Average Onion Rings'],
    owner_reply: null,
  },
  {
    id: 'rev-4',
    restaurant_id: 'rest-4',
    restaurant_name: 'Spicy Palace',
    customer_name: 'Bad Reviewer',
    rating: 1,
    comment: 'Worst place ever! The manager yelled at us and I think there was a bug in my soup!!!',
    created_at: '2026-06-16T21:40:00Z',
    flagged: true,
    status: 'FLAGGED',
    sentiment: 'NEGATIVE',
    tags: ['Rude Manager', 'Bug in Soup'],
    owner_reply: null,
  },
  {
    id: 'rev-5',
    restaurant_id: 'rest-1',
    restaurant_name: 'Golden Dragon',
    customer_name: 'Sarah Lee',
    rating: 3,
    comment: 'Decent fried rice, but nothing special. The bubble tea was way too sweet.',
    created_at: '2026-06-15T15:20:00Z',
    flagged: false,
    status: 'PENDING',
    sentiment: 'NEUTRAL',
    tags: ['Decent Fried Rice', 'Sweet Bubble Tea'],
    owner_reply: null,
  },
];

@Injectable({ providedIn: 'root' })
export class ReviewsService {
  private reviews: Review[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('quickbite_reviews');
      if (stored) {
        try {
          this.reviews = JSON.parse(stored);
        } catch {
          this.resetMocks();
        }
      } else {
        this.resetMocks();
      }
    } else {
      this.reviews = [...MOCK_REVIEWS];
    }
  }

  private resetMocks(): void {
    this.reviews = [...MOCK_REVIEWS];
    this.save();
  }

  private save(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_reviews', JSON.stringify(this.reviews));
    }
  }

  getReviews(): Observable<Review[]> {
    return of([...this.reviews]).pipe(delay(200));
  }

  moderateReview(id: string, status: 'APPROVED' | 'REJECTED' | 'FLAGGED'): Observable<Review[]> {
    const review = this.reviews.find((r) => r.id === id);
    if (review) {
      review.status = status;
      review.flagged = status === 'FLAGGED';
      this.save();
    }
    return of([...this.reviews]).pipe(delay(200));
  }

  submitReply(id: string, reply: string): Observable<Review[]> {
    const review = this.reviews.find((r) => r.id === id);
    if (review) {
      review.owner_reply = reply;
      this.save();
    }
    return of([...this.reviews]).pipe(delay(200));
  }
}
