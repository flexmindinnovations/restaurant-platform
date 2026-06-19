import 'dart:async';
import 'package:core/core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:maps/maps.dart';
import 'package:networking/networking.dart';
import 'package:realtime/realtime.dart';

class OrderDetails {
  const OrderDetails({
    required this.id,
    required this.status,
    required this.restaurantName,
    required this.destinationLat,
    required this.destinationLng,
  });

  factory OrderDetails.fromJson(Map<String, dynamic> json) {
    return OrderDetails(
      id: json['id'] as String,
      status: json['status'] as String,
      restaurantName: json['restaurant_name'] as String? ?? 'Restaurant',
      destinationLat:
          (json['destination_latitude'] as num?)?.toDouble() ?? 40.7128,
      destinationLng:
          (json['destination_longitude'] as num?)?.toDouble() ?? -74.0060,
    );
  }

  final String id;
  final String status;
  final String restaurantName;
  final double destinationLat;
  final double destinationLng;
}

// Riverpod 3.x internal family types are not cleanly exported,
// so we let Dart infer the type.
// ignore: specify_nonobvious_property_types
final orderDetailsProvider =
    FutureProvider.family<OrderDetails, String>((ref, orderId) async {
      final dio = ref.watch(dioClientProvider);
      try {
        final response = await dio.get<dynamic>('/api/v1/orders/$orderId');
        if (response.statusCode == 200 && response.data != null) {
          final envelope = response.data as Map<String, dynamic>;
          final data = envelope['data'] as Map<String, dynamic>;
          return OrderDetails.fromJson(data);
        }
      } on Exception catch (e) {
        AppLogger.warning('Failed to fetch order details: $e');
      }

      return OrderDetails(
        id: orderId,
        status: 'PREPARING',
        restaurantName: 'Burger Palace',
        destinationLat: 40.7128,
        destinationLng: -74.0060,
      );
    });

class OrderTrackingScreen extends ConsumerStatefulWidget {
  const OrderTrackingScreen({required this.orderId, super.key});

  final String orderId;

  @override
  ConsumerState<OrderTrackingScreen> createState() =>
      _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends ConsumerState<OrderTrackingScreen> {
  StreamSubscription<LatLng>? _trackingSubscription;
  LatLng? _driverLocation;

  @override
  void initState() {
    super.initState();
    _startTracking();
  }

  @override
  void dispose() {
    if (_trackingSubscription != null) {
      unawaited(_trackingSubscription!.cancel());
    }
    ref.read(orderTrackingServiceProvider).stopTracking();
    super.dispose();
  }

  void _startTracking() {
    final trackingService = ref.read(orderTrackingServiceProvider);
    try {
      _trackingSubscription = trackingService
          .trackOrder(widget.orderId)
          .listen(
            (location) {
              setState(() {
                _driverLocation = location;
              });
            },
            onError: (dynamic err) {
              AppLogger.error('Error tracking order via WebSocket', err);
            },
          );
    } on Exception catch (e) {
      AppLogger.warning('WebSocket connection failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final orderAsync = ref.watch(orderDetailsProvider(widget.orderId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Track Order'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.goNamed('home'),
        ),
      ),
      body: orderAsync.when(
        data: (details) {
          final status = _driverLocation != null
              ? 'OUT_FOR_DELIVERY'
              : details.status;

          if (status == 'DELIVERED') {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              context.go('/review/${details.id}');
            });
          }

          final initialCenter = LatLng(
            latitude: details.destinationLat,
            longitude: details.destinationLng,
          );

          return Column(
            children: [
              Expanded(
                child: TrackingMap(
                  initialCenter: initialCenter,
                  driverLocation:
                      _driverLocation ??
                      LatLng(
                        latitude: details.destinationLat + 0.003,
                        longitude: details.destinationLng + 0.003,
                      ),
                  destinationLocation: initialCenter,
                  sourceLocation: LatLng(
                    latitude: details.destinationLat - 0.002,
                    longitude: details.destinationLng - 0.002,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(24),
                  ),
                  boxShadow: const [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 10,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                details.restaurantName,
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineSmall,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Order Status: $status',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Theme.of(context).colorScheme.primary,
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (status != 'DELIVERED')
                          ElevatedButton(
                            onPressed: () {
                              context.go('/review/${details.id}');
                            },
                            child: const Text('Simulate Delivery'),
                          )
                        else
                          const CircularProgressIndicator(),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),
                    const Row(
                      children: [
                        Icon(Icons.directions_bike, color: Colors.green),
                        SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Your rider is carrying your meal and is '
                            'on the way!',
                            style: TextStyle(fontSize: 14),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
