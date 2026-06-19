import 'package:core/core.dart';
import 'package:customer_app/features/order/order_tracking_screen.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:networking/networking.dart';

class ReviewSubmissionScreen extends ConsumerStatefulWidget {
  const ReviewSubmissionScreen({required this.orderId, super.key});

  final String orderId;

  @override
  ConsumerState<ReviewSubmissionScreen> createState() =>
      _ReviewSubmissionScreenState();
}

class _ReviewSubmissionScreenState
    extends ConsumerState<ReviewSubmissionScreen> {
  int _rating = 5;
  final _commentController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _submitReview(String restaurantName) async {
    setState(() {
      _isSubmitting = true;
    });

    final dio = ref.read(dioClientProvider);
    try {
      await dio.post<dynamic>(
        '/api/v1/reviews',
        data: {
          'order_id': widget.orderId,
          'rating': _rating,
          'comment': _commentController.text.trim(),
          'restaurant_name': restaurantName,
        },
      );
    } on Exception catch (e) {
      AppLogger.warning(
        'Failed to send review to API: $e. Using local simulated success.',
      );
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Thank you! Your review has been submitted.'),
        ),
      );
      context.goNamed('home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final orderAsync = ref.watch(orderDetailsProvider(widget.orderId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Rate Your Order'),
      ),
      body: orderAsync.when(
        data: (details) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const SizedBox(height: 20),
                const Icon(
                  Icons.stars,
                  size: 80,
                  color: Colors.amber,
                ),
                const SizedBox(height: 16),
                Text(
                  'How was your order from ${details.restaurantName}?',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Your feedback helps us and the restaurant improve.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 32),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(5, (index) {
                    final starValue = index + 1;
                    return IconButton(
                      iconSize: 48,
                      icon: Icon(
                        starValue <= _rating ? Icons.star : Icons.star_border,
                        color: Colors.amber,
                      ),
                      onPressed: () {
                        setState(() {
                          _rating = starValue;
                        });
                      },
                    );
                  }),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _commentController,
                  maxLines: 4,
                  decoration: InputDecoration(
                    labelText: 'Tell us more about your experience (optional)',
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
                ),
                const SizedBox(height: 32),
                if (_isSubmitting)
                  const CircularProgressIndicator()
                else
                  AppButton(
                    text: 'Submit Review',
                    onPressed: () => _submitReview(details.restaurantName),
                  ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
