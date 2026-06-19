import 'package:customer_app/features/auth/auth_screen.dart';
import 'package:customer_app/features/cart/cart_screen.dart';
import 'package:customer_app/features/home/ai_search_screen.dart';
import 'package:customer_app/features/home/home_screen.dart';
import 'package:customer_app/features/order/order_tracking_screen.dart';
import 'package:customer_app/features/order/review_submission_screen.dart';
import 'package:customer_app/features/profile/profile_screen.dart';
import 'package:customer_app/features/restaurant/restaurant_detail_screen.dart';
import 'package:customer_app/features/splash/splash_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/auth',
        name: 'auth',
        builder: (context, state) => const AuthScreen(),
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/restaurant/:id',
        name: 'restaurant',
        builder: (context, state) {
          final rest = state.extra! as Restaurant;
          return RestaurantDetailScreen(restaurant: rest);
        },
      ),
      GoRoute(
        path: '/cart',
        name: 'cart',
        builder: (context, state) => const CartScreen(),
      ),
      GoRoute(
        path: '/tracking/:id',
        name: 'tracking',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return OrderTrackingScreen(orderId: id);
        },
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/history',
        name: 'history',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/ai-search',
        name: 'ai-search',
        builder: (context, state) {
          final query = state.uri.queryParameters['q'] ?? '';
          return AISearchScreen(query: query);
        },
      ),
      GoRoute(
        path: '/review/:id',
        name: 'review',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return ReviewSubmissionScreen(orderId: id);
        },
      ),
    ],
  );
});
