import 'dart:async';
import 'package:core/core.dart';
import 'package:customer_app/features/cart/cart_provider.dart';
import 'package:customer_app/features/home/home_screen.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:networking/networking.dart';

class MenuItemModel {
  const MenuItemModel({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.isAvailable,
    this.imageUrl,
  });

  factory MenuItemModel.fromJson(Map<String, dynamic> json) {
    return MenuItemModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      price: (json['price_amount'] as num).toDouble(),
      imageUrl: json['image_url'] as String?,
      isAvailable: json['is_available'] as bool? ?? true,
    );
  }

  final String id;
  final String name;
  final String description;
  final double price;
  final String? imageUrl;
  final bool isAvailable;
}

class MenuCategoryModel {
  const MenuCategoryModel({
    required this.id,
    required this.name,
    required this.items,
  });

  final String id;
  final String name;
  final List<MenuItemModel> items;
}

class ModifierModel {
  const ModifierModel({
    required this.id,
    required this.name,
    required this.priceAdjustment,
  });

  final String id;
  final String name;
  final double priceAdjustment;
}

class ModifierGroupModel {
  const ModifierGroupModel({
    required this.id,
    required this.name,
    required this.selectionType,
    required this.isRequired,
    required this.modifiers,
  });

  final String id;
  final String name;
  final String selectionType;
  final bool isRequired;
  final List<ModifierModel> modifiers;
}

// Riverpod 3.x internal family types are not cleanly exported,
// so we let Dart infer the type.
// ignore: specify_nonobvious_property_types
final restaurantMenuProvider =
    FutureProvider.family<List<MenuCategoryModel>, String>(
        (ref, restaurantId) async {
    final dio = ref.watch(dioClientProvider);
    try {
      final response = await dio.get<dynamic>(
        '/api/v1/menus?restaurant_id=$restaurantId',
      );
      if (response.statusCode == 200 && response.data != null) {
        final envelope = response.data as Map<String, dynamic>;
        final data = envelope['data'] as Map<String, dynamic>;
        final menus = data['items'] as List<dynamic>? ?? [];

        if (menus.isNotEmpty) {
          final firstMenu = menus[0] as Map<String, dynamic>;
          final firstMenuId = firstMenu['id'] as String;
          final itemsResp = await dio.get<dynamic>(
            '/api/v1/menus/$firstMenuId/items',
          );
          if (itemsResp.statusCode == 200 && itemsResp.data != null) {
            final itemsEnv = itemsResp.data as Map<String, dynamic>;
            final itemsData = itemsEnv['data'] as Map<String, dynamic>;
            final items = itemsData['items'] as List<dynamic>? ?? [];

            final categories = <String, List<MenuItemModel>>{};
            for (final item in items) {
              final itemMap = item as Map<String, dynamic>;
              final model = MenuItemModel.fromJson(itemMap);
              final catId = itemMap['category_id'] as String? ?? 'General';
              categories.putIfAbsent(catId, () => []).add(model);
            }

            return categories.entries.map((e) {
              return MenuCategoryModel(
                id: e.key,
                name: e.key == 'General' ? 'General' : 'Category',
                items: e.value,
              );
            }).toList();
          }
        }
      }
    } on Exception catch (e) {
      AppLogger.warning('Failed to fetch menus: $e');
    }

    return const [
      MenuCategoryModel(
        id: 'cat-1',
        name: 'Popular Items',
        items: [
          MenuItemModel(
            id: 'item-1',
            name: 'Signature Burger',
            description:
                '1/2 lb beef patty with cheddar cheese, lettuce, tomato, '
                'and house sauce.',
            price: 12.99,
            isAvailable: true,
          ),
          MenuItemModel(
            id: 'item-2',
            name: 'Classic Margherita Pizza',
            description:
                'San Marzano tomatoes, fresh mozzarella, fresh basil, '
                'and extra virgin olive oil.',
            price: 14.5,
            isAvailable: true,
          ),
        ],
      ),
      MenuCategoryModel(
        id: 'cat-2',
        name: 'Sides & Extras',
        items: [
          MenuItemModel(
            id: 'item-3',
            name: 'Truffle Fries',
            description:
                'Golden crispy fries tossed in truffle oil, parmesan, '
                'and herbs.',
            price: 5.99,
            isAvailable: true,
          ),
          MenuItemModel(
            id: 'item-4',
            name: 'Garlic Breadsticks',
            description:
                'Warm breadsticks brushed with garlic butter and '
                'served with marinara.',
            price: 4.5,
            isAvailable: true,
          ),
        ],
      ),
    ];
  },
);

class RestaurantDetailScreen extends ConsumerWidget {
  const RestaurantDetailScreen({required this.restaurant, super.key});

  final Restaurant restaurant;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final menuAsync = ref.watch(restaurantMenuProvider(restaurant.id));

    return Scaffold(
      appBar: AppBar(
        title: Text(restaurant.name),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).cardColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      restaurant.name,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    if (restaurant.isVerified) ...[
                      const SizedBox(width: 8),
                      const Icon(Icons.verified, color: Colors.blue, size: 24),
                    ],
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  restaurant.description,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined, size: 18),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text('${restaurant.street}, ${restaurant.city}'),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: menuAsync.when(
              data: (categories) {
                return ListView.builder(
                  itemCount: categories.length,
                  itemBuilder: (context, index) {
                    final category = categories[index];
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(
                            left: 16,
                            top: 16,
                            bottom: 8,
                          ),
                          child: Text(
                            category.name,
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(
                                  color: AppColors.primaryLight,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                        ),
                        ...category.items.map((item) {
                          return ListTile(
                            title: Text(item.name),
                            subtitle: Text(item.description),
                            trailing: Text(
                              '\$${item.price.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            enabled: item.isAvailable,
                            onTap: () {
                              unawaited(
                                showDialog<void>(
                                  context: context,
                                  builder: (_) => MenuItemCustomizeDialog(
                                    restaurantId: restaurant.id,
                                    item: item,
                                  ),
                                ),
                              );
                            },
                          );
                        }),
                      ],
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, s) => Center(child: Text('Error: $e')),
            ),
          ),
        ],
      ),
    );
  }
}

class MenuItemCustomizeDialog extends ConsumerStatefulWidget {
  const MenuItemCustomizeDialog({
    required this.restaurantId,
    required this.item,
    super.key,
  });

  final String restaurantId;
  final MenuItemModel item;

  @override
  ConsumerState<MenuItemCustomizeDialog> createState() =>
      _MenuItemCustomizeDialogState();
}

class _MenuItemCustomizeDialogState
    extends ConsumerState<MenuItemCustomizeDialog> {
  int _quantity = 1;
  final _selectedModifiers = <String>{};

  final _modifierGroups = const [
    ModifierGroupModel(
      id: 'mod-g-1',
      name: 'Size',
      selectionType: 'SINGLE',
      isRequired: true,
      modifiers: [
        ModifierModel(id: 'mod-1', name: 'Regular', priceAdjustment: 0),
        ModifierModel(id: 'mod-2', name: 'Large', priceAdjustment: 2),
      ],
    ),
    ModifierGroupModel(
      id: 'mod-g-2',
      name: 'Add-ons',
      selectionType: 'MULTIPLE',
      isRequired: false,
      modifiers: [
        ModifierModel(id: 'mod-3', name: 'Extra Cheese', priceAdjustment: 1.5),
        ModifierModel(id: 'mod-4', name: 'Bacon', priceAdjustment: 2),
      ],
    ),
  ];

  @override
  void initState() {
    super.initState();
    for (final group in _modifierGroups) {
      if (group.isRequired && group.modifiers.isNotEmpty) {
        _selectedModifiers.add(group.modifiers.first.id);
      }
    }
  }

  double get _totalPrice {
    var base = widget.item.price;
    for (final group in _modifierGroups) {
      for (final mod in group.modifiers) {
        if (_selectedModifiers.contains(mod.id)) {
          base += mod.priceAdjustment;
        }
      }
    }
    return base * _quantity;
  }

  void _onModifierSelected(
    ModifierGroupModel group,
    ModifierModel modifier,
    bool selected,
  ) {
    setState(() {
      if (group.selectionType == 'SINGLE') {
        if (selected) {
          for (final m in group.modifiers) {
            _selectedModifiers.remove(m.id);
          }
          _selectedModifiers.add(modifier.id);
        }
      } else {
        if (selected) {
          _selectedModifiers.add(modifier.id);
        } else {
          _selectedModifiers.remove(modifier.id);
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.item.name),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.item.description),
            const SizedBox(height: 16),
            ..._modifierGroups.map((group) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Text(
                      '${group.name}${group.isRequired ? " (Required)" : ""}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  ...group.modifiers.map((mod) {
                    final isSelected = _selectedModifiers.contains(mod.id);
                    final priceAdj = mod.priceAdjustment.toStringAsFixed(2);
                    return InkWell(
                      onTap: () {
                        _onModifierSelected(group, mod, !isSelected);
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Row(
                          children: [
                            Icon(
                              isSelected
                                  ? Icons.radio_button_checked
                                  : Icons.radio_button_off,
                              color: isSelected
                                  ? Theme.of(context).colorScheme.primary
                                  : null,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                '${mod.name} (+\$$priceAdj)',
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                  const Divider(),
                ],
              );
            }),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Quantity',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove_circle_outline),
                      onPressed: _quantity > 1
                          ? () => setState(() => _quantity--)
                          : null,
                    ),
                    Text(
                      '$_quantity',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline),
                      onPressed: () => setState(() => _quantity++),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () async {
            final modifierNames = _modifierGroups
                .expand((g) => g.modifiers)
                .where((m) => _selectedModifiers.contains(m.id))
                .map((m) => m.name)
                .join(', ');

            await ref
                .read(cartProvider.notifier)
                .addToCart(
                  restaurantId: widget.restaurantId,
                  menuItemId: widget.item.id,
                  name: widget.item.name,
                  price: widget.item.price,
                  quantity: _quantity,
                  specialInstructions: modifierNames.isNotEmpty
                      ? 'Selected: $modifierNames'
                      : null,
                );

            if (context.mounted) {
              Navigator.of(context).pop();
            }
          },
          child: Text('Add to Cart - \$${_totalPrice.toStringAsFixed(2)}'),
        ),
      ],
    );
  }
}
