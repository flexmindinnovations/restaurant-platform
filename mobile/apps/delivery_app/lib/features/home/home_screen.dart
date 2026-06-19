import 'dart:async';
import 'package:authentication/authentication.dart';
import 'package:core/core.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:maps/maps.dart';
import 'package:realtime/realtime.dart';

class DeliveryOrder {
  const DeliveryOrder({
    required this.id,
    required this.orderNumber,
    required this.restaurantName,
    required this.restaurantAddress,
    required this.deliveryAddress,
    required this.restaurantLat,
    required this.restaurantLng,
    required this.destinationLat,
    required this.destinationLng,
    required this.fee,
  });

  final String id;
  final String orderNumber;
  final String restaurantName;
  final String restaurantAddress;
  final String deliveryAddress;
  final double restaurantLat;
  final double restaurantLng;
  final double destinationLat;
  final double destinationLng;
  final double fee;
}

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  bool _isOnline = false;
  DeliveryOrder? _activeOrder;
  String _activeStatus = 'ACCEPTED'; // ACCEPTED, PICKED_UP, DELIVERED

  Timer? _positionTimer;
  StreamSubscription<LatLng>? _localLocationSubscription;
  LatLng? _currentLocation;

  // Earnings Stats
  double _todayEarnings = 42.5;
  int _completedDeliveries = 4;

  @override
  void dispose() {
    _stopLocationUpdates();
    super.dispose();
  }

  void _startLocationUpdates() {
    final locationService = ref.read(locationServiceProvider);
    final wsClient = ref.read(webSocketClientProvider);

    unawaited(
      locationService
          .getCurrentLocation()
          .then((loc) {
            if (mounted) {
              setState(() {
                _currentLocation = loc;
              });
            }
          })
          .catchError((dynamic e) {
            AppLogger.warning('Failed to get location: $e');
          }),
    );

    _localLocationSubscription = locationService.getLocationStream().listen((
      loc,
    ) {
      if (mounted) {
        setState(() {
          _currentLocation = loc;
        });
      }
    });

    _positionTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      if (_currentLocation != null && _activeOrder != null) {
        AppLogger.info(
          'Sending location: '
          '${_currentLocation!.latitude}, ${_currentLocation!.longitude}',
        );
        try {
          wsClient.sendMessage({
            'latitude': _currentLocation!.latitude,
            'longitude': _currentLocation!.longitude,
            'status': _activeStatus,
          });
        } on Exception catch (e) {
          AppLogger.warning('Failed to send updates: $e');
        }
      }
    });
  }

  void _stopLocationUpdates() {
    _positionTimer?.cancel();
    if (_localLocationSubscription != null) {
      unawaited(_localLocationSubscription!.cancel());
    }
  }

  void _simulateIncomingOrder() {
    if (!_isOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('You must be online to receive orders.')),
      );
      return;
    }

    const mockOrder = DeliveryOrder(
      id: 'ord-998',
      orderNumber: 'ORD-9987',
      restaurantName: 'Burger Palace',
      restaurantAddress: '123 Main St',
      deliveryAddress: '456 Oak Ave, Apt 4B',
      restaurantLat: 40.715,
      restaurantLng: -74.008,
      destinationLat: 40.7128,
      destinationLng: -74.006,
      fee: 6.5,
    );

    unawaited(
      showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => IncomingAssignmentModal(
          order: mockOrder,
          onAccept: () {
            setState(() {
              _activeOrder = mockOrder;
              _activeStatus = 'ACCEPTED';
            });
            _startLocationUpdates();
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Courier Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              _stopLocationUpdates();
              await ref.read(authStateProvider.notifier).logout();
              if (context.mounted) {
                context.goNamed('auth');
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            AppCard(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Availability Status',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        _isOnline ? 'Online - Receiving orders' : 'Offline',
                        style: TextStyle(
                          color: _isOnline ? Colors.green : Colors.grey,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  Switch(
                    value: _isOnline,
                    onChanged: (val) {
                      setState(() {
                        _isOnline = val;
                        if (!_isOnline) {
                          _stopLocationUpdates();
                          _activeOrder = null;
                        }
                      });
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            if (_activeOrder != null) ...[
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Active Delivery: ${_activeOrder!.orderNumber}',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        Chip(
                          label: Text(_activeStatus),
                          backgroundColor: AppColors.primaryContainerLight,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Pickup: ${_activeOrder!.restaurantName}'),
                    Text(
                      'Restaurant Address: ${_activeOrder!.restaurantAddress}',
                    ),
                    const SizedBox(height: 4),
                    Text('Dropoff: ${_activeOrder!.deliveryAddress}'),
                    const Divider(),
                    SizedBox(
                      height: 200,
                      child: TrackingMap(
                        initialCenter: LatLng(
                          latitude: _activeOrder!.restaurantLat,
                          longitude: _activeOrder!.restaurantLng,
                        ),
                        driverLocation:
                            _currentLocation ??
                            LatLng(
                              latitude: _activeOrder!.restaurantLat,
                              longitude: _activeOrder!.restaurantLng,
                            ),
                        destinationLocation: LatLng(
                          latitude: _activeOrder!.destinationLat,
                          longitude: _activeOrder!.destinationLng,
                        ),
                        sourceLocation: LatLng(
                          latitude: _activeOrder!.restaurantLat,
                          longitude: _activeOrder!.restaurantLng,
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        if (_activeStatus == 'ACCEPTED')
                          Expanded(
                            child: AppButton(
                              text: 'Picked Up',
                              onPressed: () {
                                setState(() {
                                  _activeStatus = 'PICKED_UP';
                                });
                              },
                            ),
                          ),
                        if (_activeStatus == 'PICKED_UP')
                          Expanded(
                            child: AppButton(
                              text: 'Delivered',
                              onPressed: () {
                                setState(() {
                                  _todayEarnings += _activeOrder!.fee;
                                  _completedDeliveries += 1;
                                  _activeOrder = null;
                                  _stopLocationUpdates();
                                });
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Delivery completed!'),
                                  ),
                                );
                              },
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Earnings Summary',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        children: [
                          const Text("Today's Income"),
                          const SizedBox(height: 4),
                          Text(
                            '\$${_todayEarnings.toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        children: [
                          const Text('Deliveries'),
                          const SizedBox(height: 4),
                          Text(
                            '$_completedDeliveries',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            if (_isOnline && _activeOrder == null)
              AppButton(
                text: 'Simulate Incoming Order',
                onPressed: _simulateIncomingOrder,
              ),
          ],
        ),
      ),
    );
  }
}

class IncomingAssignmentModal extends StatefulWidget {
  const IncomingAssignmentModal({
    required this.order,
    required this.onAccept,
    super.key,
  });

  final DeliveryOrder order;
  final VoidCallback onAccept;

  @override
  State<IncomingAssignmentModal> createState() =>
      _IncomingAssignmentModalState();
}

class _IncomingAssignmentModalState extends State<IncomingAssignmentModal> {
  int _secondsRemaining = 30;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() {
          _secondsRemaining--;
        });
      } else {
        _timer?.cancel();
        Navigator.of(context).pop();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.assignment_late, color: Colors.orange),
          SizedBox(width: 8),
          Text('New Assignment'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Restaurant: ${widget.order.restaurantName}'),
          Text('Pickup Address: ${widget.order.restaurantAddress}'),
          const SizedBox(height: 8),
          Text('Delivery Address: ${widget.order.deliveryAddress}'),
          const Divider(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Earning Fee:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                '\$${widget.order.fee.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              'Accept in: $_secondsRemaining seconds',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: _secondsRemaining / 30,
            valueColor: const AlwaysStoppedAnimation<Color>(Colors.red),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            _timer?.cancel();
            Navigator.of(context).pop();
          },
          child: const Text('Reject'),
        ),
        ElevatedButton(
          onPressed: () {
            _timer?.cancel();
            widget.onAccept();
            Navigator.of(context).pop();
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            foregroundColor: Colors.white,
          ),
          child: const Text('Accept'),
        ),
      ],
    );
  }
}
