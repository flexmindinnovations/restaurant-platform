import 'dart:async';
import 'package:core/core.dart';
import 'package:customer_app/features/cart/cart_provider.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:localization/localization.dart';
import 'package:networking/networking.dart';

class Restaurant {
  const Restaurant({
    required this.id,
    required this.name,
    required this.description,
    required this.street,
    required this.city,
    required this.cuisineTypes,
    required this.isVerified,
    required this.latitude,
    required this.longitude,
  });

  factory Restaurant.fromJson(Map<String, dynamic> json) {
    final rawCuisine = json['cuisine_types'] as List<dynamic>?;
    return Restaurant(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      street: json['address_street'] as String? ?? '',
      city: json['address_city'] as String? ?? '',
      cuisineTypes: rawCuisine?.map((e) => e.toString()).toList() ?? [],
      isVerified: json['is_verified'] as bool? ?? false,
      latitude: (json['address_latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['address_longitude'] as num?)?.toDouble() ?? 0.0,
    );
  }

  final String id;
  final String name;
  final String description;
  final String street;
  final String city;
  final List<String> cuisineTypes;
  final bool isVerified;
  final double latitude;
  final double longitude;
}

final restaurantsProvider = FutureProvider<List<Restaurant>>((ref) async {
  final dio = ref.watch(dioClientProvider);
  try {
    final response = await dio.get<dynamic>('/api/v1/restaurants');
    if (response.statusCode == 200 && response.data != null) {
      final envelope = response.data as Map<String, dynamic>;
      final data = envelope['data'] as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => Restaurant.fromJson(e as Map<String, dynamic>))
          .toList();
    }
  } on Exception catch (e) {
    AppLogger.warning('Failed to fetch restaurants: $e');
  }

  return const [
    Restaurant(
      id: 'd9e03d7c-bb49-43c3-88bb-8b770549cda8',
      name: 'Burger Palace',
      description: 'Gourmet burgers and delicious hand-cut fries.',
      street: '123 Main St',
      city: 'Metro City',
      cuisineTypes: ['Burgers', 'Fast Food'],
      isVerified: true,
      latitude: 40.7128,
      longitude: -74.0060,
    ),
    Restaurant(
      id: 'f70fb67f-4bdf-4841-948f-3cc1d56e792c',
      name: 'Pizzeria Bella',
      description: 'Authentic wood-fired Neapolitan pizzas.',
      street: '456 Oak Ave',
      city: 'Metro City',
      cuisineTypes: ['Pizza', 'Italian'],
      isVerified: true,
      latitude: 40.7150,
      longitude: -74.0080,
    ),
    Restaurant(
      id: '868dfd6a-4ee2-4df3-8ea9-a864a75ab28a',
      name: 'Taco Loco',
      description: 'Tasty tacos, burritos, and fresh guacamole.',
      street: '789 Pine Rd',
      city: 'Metro City',
      cuisineTypes: ['Mexican', 'Street Food'],
      isVerified: true,
      latitude: 40.7110,
      longitude: -74.0040,
    ),
  ];
});

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final _searchController = TextEditingController();
  String _selectedFilter = 'All';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final restaurantsAsync = ref.watch(restaurantsProvider);
    final cart = ref.watch(cartProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n('app_title')),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => context.push('/history'),
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push('/profile'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: AppTextField(
              controller: _searchController,
              labelText: 'Search Restaurants',
              prefixIcon: const Icon(Icons.search),
              onChanged: (_) => setState(() {}),
            ),
          ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children:
                  [
                    'All',
                    'Burgers',
                    'Pizza',
                    'Italian',
                    'Mexican',
                  ].map((cuisine) {
                    final isSelected = _selectedFilter == cuisine;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: FilterChip(
                        label: Text(cuisine),
                        selected: isSelected,
                        onSelected: (selected) {
                          setState(() {
                            _selectedFilter = cuisine;
                          });
                        },
                      ),
                    );
                  }).toList(),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: restaurantsAsync.when(
              data: (list) {
                final query = _searchController.text.toLowerCase();
                final filtered = list.where((r) {
                  final matchesSearch =
                      r.name.toLowerCase().contains(query) ||
                      r.description.toLowerCase().contains(query);
                  final matchesCuisine =
                      _selectedFilter == 'All' ||
                      r.cuisineTypes.contains(_selectedFilter);
                  return matchesSearch && matchesCuisine;
                }).toList();

                if (filtered.isEmpty) {
                  return const Center(child: Text('No restaurants found.'));
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final restaurant = filtered[index];
                    return GestureDetector(
                      onTap: () {
                        unawaited(
                          context.push(
                            '/restaurant/${restaurant.id}',
                            extra: restaurant,
                          ),
                        );
                      },
                      child: AppCard(
                        padding: const EdgeInsets.all(12),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                color: AppColors.primaryContainerLight,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(
                                Icons.restaurant,
                                size: 40,
                                color: AppColors.primaryLight,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        restaurant.name,
                                        style: Theme.of(
                                          context,
                                        ).textTheme.titleLarge,
                                      ),
                                      if (restaurant.isVerified) ...[
                                        const SizedBox(width: 4),
                                        const Icon(
                                          Icons.verified,
                                          size: 16,
                                          color: Colors.blue,
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    restaurant.description,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: Theme.of(
                                      context,
                                    ).textTheme.bodyMedium,
                                  ),
                                  const SizedBox(height: 8),
                                  Wrap(
                                    spacing: 4,
                                    children: restaurant.cuisineTypes.map((c) {
                                      return Chip(
                                        label: Text(
                                          c,
                                          style: const TextStyle(fontSize: 10),
                                        ),
                                        padding: EdgeInsets.zero,
                                        materialTapTargetSize:
                                            MaterialTapTargetSize.shrinkWrap,
                                      );
                                    }).toList(),
                                  ),
                                ],
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
          ),
        ],
      ),
      floatingActionButton: cart.items.isNotEmpty
          ? FloatingActionButton.extended(
              backgroundColor: AppColors.primaryLight,
              foregroundColor: Colors.white,
              onPressed: () => context.push('/cart'),
              label: Text('Cart (${cart.items.length})'),
              icon: const Icon(Icons.shopping_cart),
            )
          : null,
    );
  }
}
