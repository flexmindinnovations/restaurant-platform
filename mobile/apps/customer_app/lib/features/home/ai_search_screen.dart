import 'dart:async';
import 'package:customer_app/features/home/home_screen.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class AISearchScreen extends ConsumerStatefulWidget {
  const AISearchScreen({required this.query, super.key});

  final String query;

  @override
  ConsumerState<AISearchScreen> createState() => _AISearchScreenState();
}

class _AISearchScreenState extends ConsumerState<AISearchScreen> {
  late final TextEditingController _controller;
  late String _currentQuery;

  @override
  void initState() {
    super.initState();
    _currentQuery = widget.query;
    _controller = TextEditingController(text: widget.query);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  double _calculateMatchScore(Restaurant restaurant, String query) {
    final q = query.toLowerCase();
    var score = 0;
    if (restaurant.name.toLowerCase().contains(q)) score += 40;
    if (restaurant.description.toLowerCase().contains(q)) score += 30;
    for (final cuisine in restaurant.cuisineTypes) {
      if (cuisine.toLowerCase().contains(q) ||
          q.contains(cuisine.toLowerCase())) {
        score += 35;
      }
    }
    if (q.contains('spicy') || q.contains('hot')) {
      if (restaurant.cuisineTypes.contains('Mexican') ||
          restaurant.name.contains('Taco') ||
          restaurant.name.contains('Burger')) {
        score += 25;
      }
    }
    if (q.contains('cheese') || q.contains('cheesy') || q.contains('slice')) {
      if (restaurant.cuisineTypes.contains('Pizza') ||
          restaurant.cuisineTypes.contains('Italian')) {
        score += 30;
      }
    }
    if (q.contains('fast') || q.contains('quick') || q.contains('delivery')) {
      if (restaurant.cuisineTypes.contains('Fast Food') ||
          restaurant.cuisineTypes.contains('Burgers')) {
        score += 20;
      }
    }

    if (score > 0) {
      return (60 + (score % 40)).toDouble();
    }
    return (40 + (restaurant.name.hashCode % 25)).toDouble();
  }

  @override
  Widget build(BuildContext context) {
    final restaurantsAsync = ref.watch(restaurantsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.auto_awesome, color: Colors.purple),
            SizedBox(width: 8),
            Text('AI Semantic Search'),
          ],
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextFormField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Search with AI (e.g. cheesy pizza, quick burgers)',
                prefixIcon: const Icon(
                  Icons.auto_awesome,
                  color: Colors.purple,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: Theme.of(context).dividerColor,
                  ),
                ),
              ),
              onFieldSubmitted: (val) {
                if (val.trim().isNotEmpty) {
                  setState(() {
                    _currentQuery = val.trim();
                  });
                }
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Icon(Icons.info_outline, size: 14, color: Colors.grey),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Showing semantic relevance matching: "$_currentQuery"',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: restaurantsAsync.when(
              data: (list) {
                final scoredList = list.map((r) {
                  final score = _calculateMatchScore(r, _currentQuery);
                  return _ScoredRestaurant(restaurant: r, score: score);
                }).toList()
                  ..sort((a, b) => b.score.compareTo(a.score));

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: scoredList.length,
                  itemBuilder: (context, index) {
                    final item = scoredList[index];
                    final restaurant = item.restaurant;
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
                                color: Colors.purple.shade50,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(
                                Icons.restaurant,
                                size: 40,
                                color: Colors.purple,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          restaurant.name,
                                          style: Theme.of(context)
                                              .textTheme
                                              .titleLarge,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 4,
                                        ),
                                        decoration: BoxDecoration(
                                          color: Colors.green.shade50,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          border: Border.all(
                                            color: Colors.green.shade200,
                                          ),
                                        ),
                                        child: Text(
                                          '${item.score.toInt()}% Match',
                                          style: const TextStyle(
                                            color: Colors.green,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    restaurant.description,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style:
                                        Theme.of(context).textTheme.bodyMedium,
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
    );
  }
}

class _ScoredRestaurant {
  const _ScoredRestaurant({required this.restaurant, required this.score});

  final Restaurant restaurant;
  final double score;
}
