import 'package:authentication/authentication.dart';
import 'package:core/core.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:networking/networking.dart';

class PastOrder {
  const PastOrder({
    required this.id,
    required this.orderNumber,
    required this.totalAmount,
    required this.status,
    required this.placedAt,
  });

  factory PastOrder.fromJson(Map<String, dynamic> json) {
    return PastOrder(
      id: json['id'] as String,
      orderNumber: json['order_number'] as String,
      totalAmount: (json['total_amount'] as num).toDouble(),
      status: json['status'] as String,
      placedAt: DateTime.parse(json['placed_at'] as String),
    );
  }

  final String id;
  final String orderNumber;
  final double totalAmount;
  final String status;
  final DateTime placedAt;
}

final pastOrdersProvider = FutureProvider<List<PastOrder>>((ref) async {
  final dio = ref.watch(dioClientProvider);
  try {
    final response = await dio.get<dynamic>('/api/v1/orders');
    if (response.statusCode == 200 && response.data != null) {
      final envelope = response.data as Map<String, dynamic>;
      final data = envelope['data'] as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => PastOrder.fromJson(e as Map<String, dynamic>))
          .toList();
    }
  } on Exception catch (e) {
    AppLogger.warning('Failed to fetch past orders: $e');
  }

  return [
    PastOrder(
      id: 'order-mock-1',
      orderNumber: 'ORD-98765',
      totalAmount: 24.5,
      status: 'DELIVERED',
      placedAt: DateTime.now().subtract(const Duration(days: 2)),
    ),
    PastOrder(
      id: 'order-mock-2',
      orderNumber: 'ORD-98764',
      totalAmount: 18.99,
      status: 'DELIVERED',
      placedAt: DateTime.now().subtract(const Duration(days: 5)),
    ),
  ];
});

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  Future<void> _logout(BuildContext context, WidgetRef ref) async {
    try {
      await ref.read(authStateProvider.notifier).logout();
      if (context.mounted) {
        context.goNamed('auth');
      }
    } on Exception catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Logout failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final pastOrdersAsync = ref.watch(pastOrdersProvider);
    final profileMap = authState.userProfile;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile & History'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AppCard(
              child: Row(
                children: [
                  const CircleAvatar(
                    radius: 30,
                    backgroundColor: AppColors.primaryLight,
                    child: Icon(Icons.person, size: 40, color: Colors.white),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          profileMap?['display_name'] as String? ??
                              'Customer User',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        Text(
                          profileMap?['email'] as String? ??
                              'user@restaurant.com',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Order History',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            pastOrdersAsync.when(
              data: (orders) {
                if (orders.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 24),
                    child: Center(child: Text('No past orders.')),
                  );
                }

                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: orders.length,
                  itemBuilder: (context, index) {
                    final order = orders[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        title: Text(order.orderNumber),
                        subtitle: Text(
                          'Placed on: ${order.placedAt.month}/'
                          '${order.placedAt.day}/${order.placedAt.year}',
                        ),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              '\$${order.totalAmount.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              order.status,
                              style: TextStyle(
                                fontSize: 12,
                                color: order.status == 'DELIVERED'
                                    ? Colors.green
                                    : Colors.orange,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, s) => Center(child: Text('Error: $e')),
            ),
            const SizedBox(height: 24),
            AppButton(
              text: 'Logout',
              isOutlined: true,
              onPressed: () => _logout(context, ref),
            ),
          ],
        ),
      ),
    );
  }
}
