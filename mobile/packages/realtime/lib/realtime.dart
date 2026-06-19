import 'dart:async';
import 'dart:convert';
import 'package:core/core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:storage/storage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Client that manages WebSocket connections.
class WebSocketClient {
  WebSocketClient(this._storage);

  final LocalStorageService _storage;
  WebSocketChannel? _channel;

  /// Connect to the tracking websocket for a specific order.
  Stream<dynamic> connectToOrderTracking(String orderId) {
    final token = _storage.read<String>('access_token');
    if (token == null) {
      throw const AuthenticationException(
        'No access token found for WebSocket connection',
      );
    }

    final uri = Uri.parse(
      'ws://localhost:8000/ws/orders/$orderId/tracking?token=$token',
    );
    AppLogger.info('Connecting to WebSocket: $uri');

    _channel = WebSocketChannel.connect(uri);
    return _channel!.stream.map((event) {
      if (event is String) {
        return jsonDecode(event);
      }
      return event;
    });
  }

  /// Send message to WebSocket.
  void sendMessage(dynamic message) {
    if (_channel != null) {
      final data = message is Map || message is List
          ? jsonEncode(message)
          : message;
      _channel!.sink.add(data);
    } else {
      AppLogger.warning('Cannot send message, WebSocket is not connected.');
    }
  }

  /// Disconnect WebSocket connection.
  void disconnect() {
    if (_channel != null) {
      unawaited(_channel!.sink.close());
      _channel = null;
      AppLogger.info('WebSocket disconnected');
    }
  }
}

/// Service that tracks delivery location updates via WebSocket.
class OrderTrackingService {
  OrderTrackingService(this._wsClient);

  final WebSocketClient _wsClient;

  /// Stream order tracking location updates.
  Stream<LatLng> trackOrder(String orderId) {
    return _wsClient.connectToOrderTracking(orderId).expand<LatLng>((event) {
      try {
        if (event is Map<String, dynamic>) {
          if (event.containsKey('latitude') && event.containsKey('longitude')) {
            return [LatLng.fromJson(event)];
          }
        }
      } on Exception catch (e) {
        AppLogger.error('Error parsing tracking message: $event', e);
      }
      return const [];
    });
  }

  /// Stop tracking the order.
  void stopTracking() {
    _wsClient.disconnect();
  }
}

/// Provider for WebSocketClient.
final webSocketClientProvider = Provider<WebSocketClient>((ref) {
  final storage = ref.watch(localStorageServiceProvider);
  return WebSocketClient(storage);
});

/// Provider for OrderTrackingService.
final orderTrackingServiceProvider = Provider<OrderTrackingService>((ref) {
  final wsClient = ref.watch(webSocketClientProvider);
  return OrderTrackingService(wsClient);
});
