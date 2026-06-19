import 'dart:developer' as developer;
import 'package:meta/meta.dart';

/// Representation of geographical coordinates.
@immutable
class LatLng {
  const LatLng({required this.latitude, required this.longitude});

  factory LatLng.fromJson(Map<String, dynamic> json) {
    return LatLng(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
    );
  }

  final double latitude;
  final double longitude;

  Map<String, dynamic> toJson() => {
    'latitude': latitude,
    'longitude': longitude,
  };

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LatLng &&
          runtimeType == other.runtimeType &&
          latitude == other.latitude &&
          longitude == other.longitude;

  @override
  int get hashCode => latitude.hashCode ^ longitude.hashCode;

  @override
  String toString() => 'LatLng(latitude: $latitude, longitude: $longitude)';
}

/// Base class for all application exceptions.
@immutable
sealed class AppException implements Exception {
  const AppException(this.message, [this.details]);

  final String message;
  final dynamic details;

  @override
  String toString() =>
      'AppException: $message${details != null ? " ($details)" : ""}';
}

@immutable
class NetworkException extends AppException {
  const NetworkException(super.message, [super.details]);

  @override
  String toString() =>
      'NetworkException: $message${details != null ? " ($details)" : ""}';
}

@immutable
class AuthenticationException extends AppException {
  const AuthenticationException(super.message, [super.details]);

  @override
  String toString() =>
      'AuthenticationException: '
      '$message${details != null ? " ($details)" : ""}';
}

@immutable
class ServerException extends AppException {
  const ServerException(super.message, [super.details]);

  @override
  String toString() =>
      'ServerException: $message${details != null ? " ($details)" : ""}';
}

@immutable
class CacheException extends AppException {
  const CacheException(super.message, [super.details]);

  @override
  String toString() =>
      'CacheException: $message${details != null ? " ($details)" : ""}';
}

@immutable
class ValidationException extends AppException {
  const ValidationException(super.message, [super.details]);

  @override
  String toString() =>
      'ValidationException: $message${details != null ? " ($details)" : ""}';
}

@immutable
class UnknownException extends AppException {
  const UnknownException(super.message, [super.details]);

  @override
  String toString() =>
      'UnknownException: $message${details != null ? " ($details)" : ""}';
}

/// Pagination metadata wrapper.
class PaginationMetadata {
  const PaginationMetadata({
    required this.totalItems,
    required this.page,
    required this.size,
    required this.totalPages,
  });

  factory PaginationMetadata.fromJson(Map<String, dynamic> json) {
    return PaginationMetadata(
      totalItems: json['total_items'] as int? ?? json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      size: json['size'] as int? ?? 10,
      totalPages: json['total_pages'] as int? ?? json['pages'] as int? ?? 1,
    );
  }

  final int totalItems;
  final int page;
  final int size;
  final int totalPages;

  Map<String, dynamic> toJson() => {
    'total_items': totalItems,
    'page': page,
    'size': size,
    'total_pages': totalPages,
  };
}

/// Standard paginated response wrapper.
class PaginatedResponse<T> {
  const PaginatedResponse({
    required this.items,
    required this.metadata,
  });

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(dynamic json) fromJsonT,
  ) {
    final rawItems = json['items'] as List<dynamic>? ?? [];
    final items = rawItems.map(fromJsonT).toList();

    return PaginatedResponse<T>(
      items: items,
      metadata: PaginationMetadata.fromJson(json),
    );
  }

  final List<T> items;
  final PaginationMetadata metadata;
}

/// Structured logger for the application.
class AppLogger {
  static void debug(
    String message, [
    Object? error,
    StackTrace? stackTrace,
  ]) {
    developer.log(
      message,
      name: 'DEBUG',
      level: 500,
      error: error,
      stackTrace: stackTrace,
    );
  }

  static void info(
    String message, [
    Object? error,
    StackTrace? stackTrace,
  ]) {
    developer.log(
      message,
      name: 'INFO',
      level: 800,
      error: error,
      stackTrace: stackTrace,
    );
  }

  static void warning(
    String message, [
    Object? error,
    StackTrace? stackTrace,
  ]) {
    developer.log(
      message,
      name: 'WARNING',
      level: 900,
      error: error,
      stackTrace: stackTrace,
    );
  }

  static void error(
    String message, [
    Object? error,
    StackTrace? stackTrace,
  ]) {
    developer.log(
      message,
      name: 'ERROR',
      level: 1000,
      error: error,
      stackTrace: stackTrace,
    );
  }
}
