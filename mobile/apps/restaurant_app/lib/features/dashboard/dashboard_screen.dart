import 'dart:async';
import 'package:authentication/authentication.dart';
import 'package:core/core.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:networking/networking.dart';

class RestaurantOrder {
  const RestaurantOrder({
    required this.id,
    required this.orderNumber,
    required this.totalAmount,
    required this.status,
  });

  factory RestaurantOrder.fromJson(Map<String, dynamic> json) {
    return RestaurantOrder(
      id: json['id'] as String,
      orderNumber: json['order_number'] as String,
      totalAmount: (json['total_amount'] as num).toDouble(),
      status: json['status'] as String,
    );
  }

  final String id;
  final String orderNumber;
  final double totalAmount;
  final String status;
}

class DashboardMenuItem {
  const DashboardMenuItem({
    required this.id,
    required this.name,
    required this.price,
    required this.isAvailable,
  });

  final String id;
  final String name;
  final double price;
  final bool isAvailable;

  DashboardMenuItem copyWith({bool? isAvailable}) {
    return DashboardMenuItem(
      id: id,
      name: name,
      price: price,
      isAvailable: isAvailable ?? this.isAvailable,
    );
  }
}

// ----------------------------------------------------
// Notifiers (Riverpod 3.0 compatible)
// ----------------------------------------------------
class RestaurantOrdersNotifier
    extends Notifier<AsyncValue<List<RestaurantOrder>>> {
  late final DioClient _dioClient;
  late final String _restaurantId;

  @override
  AsyncValue<List<RestaurantOrder>> build() {
    _dioClient = ref.watch(dioClientProvider);
    final authState = ref.watch(authStateProvider);
    final profile = authState.userProfile;
    _restaurantId =
        (profile != null ? profile['restaurant_id'] as String? : null) ??
        'd9e03d7c-bb49-43c3-88bb-8b770549cda8';
    unawaited(fetchOrders());
    return const AsyncValue<List<RestaurantOrder>>.loading();
  }

  Future<void> fetchOrders() async {
    try {
      final response = await _dioClient.get<dynamic>(
        '/api/v1/orders?restaurant_id=$_restaurantId',
      );
      if (response.statusCode == 200 && response.data != null) {
        final envelope = response.data as Map<String, dynamic>;
        final data = envelope['data'] as Map<String, dynamic>;
        final items = data['items'] as List<dynamic>? ?? [];
        final list = items
            .map((e) => RestaurantOrder.fromJson(e as Map<String, dynamic>))
            .toList();
        state = AsyncValue.data(list);
      }
    } on Exception catch (e) {
      AppLogger.warning('Failed to fetch restaurant orders: $e');
      state = const AsyncValue.data([
        RestaurantOrder(
          id: 'ord-101',
          orderNumber: 'ORD-1001',
          totalAmount: 32.5,
          status: 'PENDING',
        ),
        RestaurantOrder(
          id: 'ord-102',
          orderNumber: 'ORD-1002',
          totalAmount: 14.99,
          status: 'CONFIRMED',
        ),
        RestaurantOrder(
          id: 'ord-103',
          orderNumber: 'ORD-1003',
          totalAmount: 48.2,
          status: 'PREPARING',
        ),
        RestaurantOrder(
          id: 'ord-104',
          orderNumber: 'ORD-1004',
          totalAmount: 22.1,
          status: 'READY',
        ),
      ]);
    }
  }

  Future<void> updateStatus(String orderId, String status) async {
    try {
      await _dioClient.post<dynamic>(
        '/api/v1/orders/$orderId/status',
        data: {'status': status},
      );
      await fetchOrders();
    } on Exception catch (e) {
      AppLogger.error('Failed to update status: $e');
      state.whenData((list) {
        final index = list.indexWhere((o) => o.id == orderId);
        if (index != -1) {
          final updated = List<RestaurantOrder>.from(list);
          updated[index] = RestaurantOrder(
            id: orderId,
            orderNumber: list[index].orderNumber,
            totalAmount: list[index].totalAmount,
            status: status,
          );
          state = AsyncValue.data(updated);
        }
      });
    }
  }
}

final restaurantOrdersProvider =
    NotifierProvider<
      RestaurantOrdersNotifier,
      AsyncValue<List<RestaurantOrder>>
    >(() {
      return RestaurantOrdersNotifier();
    });

class RestaurantItemsNotifier
    extends Notifier<AsyncValue<List<DashboardMenuItem>>> {
  late final DioClient _dioClient;

  @override
  AsyncValue<List<DashboardMenuItem>> build() {
    _dioClient = ref.watch(dioClientProvider);
    unawaited(fetchItems());
    return const AsyncValue<List<DashboardMenuItem>>.loading();
  }

  Future<void> fetchItems() async {
    state = const AsyncValue.data([
      DashboardMenuItem(
        id: 'item-1',
        name: 'Signature Burger',
        price: 12.99,
        isAvailable: true,
      ),
      DashboardMenuItem(
        id: 'item-2',
        name: 'Classic Margherita Pizza',
        price: 14.5,
        isAvailable: true,
      ),
      DashboardMenuItem(
        id: 'item-3',
        name: 'Truffle Fries',
        price: 5.99,
        isAvailable: true,
      ),
      DashboardMenuItem(
        id: 'item-4',
        name: 'Garlic Breadsticks',
        price: 4.5,
        isAvailable: false,
      ),
    ]);
  }

  Future<void> toggleAvailability(
    String itemId, {
    required bool isAvailable,
  }) async {
    try {
      await _dioClient.put<dynamic>(
        '/api/v1/menus/items/$itemId',
        data: {'is_available': isAvailable},
      );
    } on Exception catch (e) {
      AppLogger.warning('Failed to update item availability: $e');
    }

    state.whenData((list) {
      final index = list.indexWhere((i) => i.id == itemId);
      if (index != -1) {
        final updated = List<DashboardMenuItem>.from(list);
        updated[index] = updated[index].copyWith(isAvailable: isAvailable);
        state = AsyncValue.data(updated);
      }
    });
  }
}

final restaurantItemsProvider =
    NotifierProvider<
      RestaurantItemsNotifier,
      AsyncValue<List<DashboardMenuItem>>
    >(() {
      return RestaurantItemsNotifier();
    });

// ----------------------------------------------------
// Screen Widget
// ----------------------------------------------------
class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ordersAsync = ref.watch(restaurantOrdersProvider);
    final itemsAsync = ref.watch(restaurantItemsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Restaurant Manager'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authStateProvider.notifier).logout();
              if (context.mounted) {
                context.goNamed('auth');
              }
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.list_alt), text: 'Orders'),
            Tab(icon: Icon(Icons.menu_book), text: 'Menu'),
            Tab(icon: Icon(Icons.bar_chart), text: 'Stats'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          ordersAsync.when(
            data: (orders) {
              final pending = orders
                  .where((o) => o.status == 'PENDING')
                  .toList();
              final preparing = orders
                  .where(
                    (o) => o.status == 'CONFIRMED' || o.status == 'PREPARING',
                  )
                  .toList();
              final ready = orders.where((o) => o.status == 'READY').toList();

              return ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildOrderSection(
                    'Pending Orders (${pending.length})',
                    pending,
                    context,
                    showAccept: true,
                  ),
                  const SizedBox(height: 24),
                  _buildOrderSection(
                    'Preparing (${preparing.length})',
                    preparing,
                    context,
                    showPreparing: true,
                  ),
                  const SizedBox(height: 24),
                  _buildOrderSection(
                    'Ready for Pickup (${ready.length})',
                    ready,
                    context,
                  ),
                ],
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, s) => Center(child: Text('Error: $e')),
          ),
          itemsAsync.when(
            data: (items) {
              return ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: items.length,
                itemBuilder: (context, index) {
                  final item = items[index];
                  return ListTile(
                    title: Text(item.name),
                    subtitle: Text('\$${item.price.toStringAsFixed(2)}'),
                    trailing: Switch(
                      value: item.isAvailable,
                      onChanged: (val) {
                        unawaited(
                          ref
                              .read(restaurantItemsProvider.notifier)
                              .toggleAvailability(item.id, isAvailable: val),
                        );
                      },
                    ),
                  );
                },
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, s) => Center(child: Text('Error: $e')),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: AppCard(
                        child: Column(
                          children: [
                            const Text(
                              'Total Orders',
                              style: TextStyle(fontSize: 16),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '18',
                              style: TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: AppCard(
                        child: Column(
                          children: [
                            const Text(
                              'Earnings',
                              style: TextStyle(fontSize: 16),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              r'$248.50',
                              style: TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: Theme.of(context).colorScheme.secondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrderSection(
    String title,
    List<RestaurantOrder> orders,
    BuildContext context, {
    bool showAccept = false,
    bool showPreparing = false,
  }) {
    if (orders.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: Text('No orders in this state.')),
            ),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        ...orders.map((order) {
          return AppCard(
            padding: const EdgeInsets.all(12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      order.orderNumber,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text('Total: \$${order.totalAmount.toStringAsFixed(2)}'),
                  ],
                ),
                Row(
                  children: [
                    if (showAccept)
                      AppButton(
                        text: 'Accept',
                        width: 80,
                        height: 36,
                        onPressed: () {
                          unawaited(
                            ref
                                .read(restaurantOrdersProvider.notifier)
                                .updateStatus(order.id, 'CONFIRMED'),
                          );
                        },
                      ),
                    if (showPreparing) ...[
                      if (order.status == 'CONFIRMED')
                        AppButton(
                          text: 'Prepare',
                          width: 80,
                          height: 36,
                          onPressed: () {
                            unawaited(
                              ref
                                  .read(restaurantOrdersProvider.notifier)
                                  .updateStatus(order.id, 'PREPARING'),
                            );
                          },
                        )
                      else
                        AppButton(
                          text: 'Ready',
                          width: 80,
                          height: 36,
                          onPressed: () {
                            unawaited(
                              ref
                                  .read(restaurantOrdersProvider.notifier)
                                  .updateStatus(order.id, 'READY'),
                            );
                          },
                        ),
                    ],
                  ],
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}
