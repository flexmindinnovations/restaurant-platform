import 'dart:async';
import 'package:core/core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:networking/networking.dart';

class LocalCartItem {
  const LocalCartItem({
    required this.menuItemId,
    required this.name,
    required this.unitPrice,
    required this.quantity,
    this.specialInstructions,
  });

  final String menuItemId;
  final String name;
  final double unitPrice;
  final int quantity;
  final String? specialInstructions;

  double get subtotal => unitPrice * quantity;

  LocalCartItem copyWith({
    int? quantity,
    String? specialInstructions,
  }) {
    return LocalCartItem(
      menuItemId: menuItemId,
      name: name,
      unitPrice: unitPrice,
      quantity: quantity ?? this.quantity,
      specialInstructions: specialInstructions ?? this.specialInstructions,
    );
  }
}

class LocalCart {
  const LocalCart({
    this.restaurantId,
    this.items = const [],
    this.totalAmount = 0,
  });

  final String? restaurantId;
  final List<LocalCartItem> items;
  final double totalAmount;

  LocalCart copyWith({
    String? restaurantId,
    List<LocalCartItem>? items,
    double? totalAmount,
  }) {
    return LocalCart(
      restaurantId: restaurantId ?? this.restaurantId,
      items: items ?? this.items,
      totalAmount: totalAmount ?? this.totalAmount,
    );
  }
}

class CartNotifier extends Notifier<LocalCart> {
  late final DioClient _dioClient;

  @override
  LocalCart build() {
    _dioClient = ref.watch(dioClientProvider);
    unawaited(fetchCart());
    return const LocalCart();
  }

  Future<void> fetchCart() async {
    try {
      final response = await _dioClient.get<dynamic>('/api/v1/checkout/cart');
      if (response.statusCode == 200 && response.data != null) {
        final envelope = response.data as Map<String, dynamic>;
        final data = envelope['data'] as Map<String, dynamic>;
        final itemsRaw = data['items'] as List<dynamic>? ?? [];
        final items = itemsRaw.map((e) {
          final itemMap = e as Map<String, dynamic>;
          return LocalCartItem(
            menuItemId: itemMap['menu_item_id'] as String,
            name: itemMap['name'] as String,
            unitPrice: (itemMap['unit_price_amount'] as num).toDouble(),
            quantity: itemMap['quantity'] as int,
            specialInstructions: itemMap['special_instructions'] as String?,
          );
        }).toList();

        state = LocalCart(
          restaurantId: data['restaurant_id'] as String?,
          items: items,
          totalAmount: (data['total_amount'] as num).toDouble(),
        );
      }
    } on Exception catch (e) {
      AppLogger.warning('Failed to fetch cart: $e');
    }
  }

  Future<void> addToCart({
    required String restaurantId,
    required String menuItemId,
    required String name,
    required double price,
    required int quantity,
    String? specialInstructions,
  }) async {
    final updatedItems = List<LocalCartItem>.from(state.items);
    if (state.restaurantId != null && state.restaurantId != restaurantId) {
      updatedItems.clear();
      try {
        await _dioClient.delete<dynamic>('/api/v1/checkout/cart/clear');
      } on Exception catch (e) {
        AppLogger.warning('Failed to clear cart in backend: $e');
      }
    }

    try {
      final response = await _dioClient.post<dynamic>(
        '/api/v1/checkout/cart/items',
        data: {
          'menu_item_id': menuItemId,
          'quantity': quantity,
          'special_instructions': specialInstructions,
        },
      );
      if (response.statusCode == 201 || response.statusCode == 200) {
        await fetchCart();
        return;
      }
    } on Exception catch (e) {
      AppLogger.warning('Failed to add to cart in backend: $e');
    }

    final existingIndex =
        updatedItems.indexWhere((item) => item.menuItemId == menuItemId);
    if (existingIndex != -1) {
      updatedItems[existingIndex] = updatedItems[existingIndex].copyWith(
        quantity: updatedItems[existingIndex].quantity + quantity,
        specialInstructions: specialInstructions,
      );
    } else {
      updatedItems.add(LocalCartItem(
        menuItemId: menuItemId,
        name: name,
        unitPrice: price,
        quantity: quantity,
        specialInstructions: specialInstructions,
      ));
    }

    final total = updatedItems.fold<double>(
      0,
      (sum, item) => sum + item.subtotal,
    );
    state = LocalCart(
      restaurantId: restaurantId,
      items: updatedItems,
      totalAmount: total,
    );
  }

  Future<void> updateItemQuantity(String menuItemId, int quantity) async {
    try {
      final response = await _dioClient.patch<dynamic>(
        '/api/v1/checkout/cart/items/$menuItemId',
        data: {'quantity': quantity},
      );
      if (response.statusCode == 200) {
        await fetchCart();
        return;
      }
    } on Exception catch (e) {
      AppLogger.warning('Failed to update cart item: $e');
    }

    final updatedItems = List<LocalCartItem>.from(state.items);
    final index =
        updatedItems.indexWhere((item) => item.menuItemId == menuItemId);
    if (index != -1) {
      if (quantity <= 0) {
        updatedItems.removeAt(index);
        try {
          await _dioClient
              .delete<dynamic>('/api/v1/checkout/cart/items/$menuItemId');
        } on Exception catch (e) {
          AppLogger.warning('Failed to delete cart item: $e');
        }
      } else {
        updatedItems[index] = updatedItems[index].copyWith(quantity: quantity);
      }
    }

    final total = updatedItems.fold<double>(
      0,
      (sum, item) => sum + item.subtotal,
    );
    state = state.copyWith(
      items: updatedItems,
      totalAmount: total,
    );
  }

  Future<void> clearCart() async {
    try {
      await _dioClient.delete<dynamic>('/api/v1/checkout/cart/clear');
    } on Exception catch (e) {
      AppLogger.warning('Failed to clear cart: $e');
    }
    state = const LocalCart();
  }

  Future<String> placeOrder({
    required String street,
    required String city,
    required String stateName,
    required String postalCode,
    required String country,
    required double tip,
    String? notes,
  }) async {
    try {
      final response = await _dioClient.post<dynamic>(
        '/api/v1/checkout/place-order',
        data: {
          'delivery_address_street': street,
          'delivery_address_city': city,
          'delivery_address_state': stateName,
          'delivery_address_postal_code': postalCode,
          'delivery_address_country': country,
          'tip_amount': tip,
          'delivery_notes': notes,
        },
      );
      if (response.statusCode == 201 && response.data != null) {
        final envelope = response.data as Map<String, dynamic>;
        final data = envelope['data'] as Map<String, dynamic>;
        final orderId = data['order_id'] as String;
        state = const LocalCart();
        return orderId;
      }
    } on Exception catch (e) {
      AppLogger.error('Failed to place order: $e');
      rethrow;
    }
    throw const UnknownException('Failed to place order');
  }
}

final cartProvider = NotifierProvider<CartNotifier, LocalCart>(() {
  return CartNotifier();
});
