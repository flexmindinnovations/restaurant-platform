import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_ce_flutter/hive_ce_flutter.dart';

/// Service for managing local key-value storage backed by Hive.
class LocalStorageService {
  LocalStorageService(this._box);

  final Box<dynamic> _box;

  static const String _defaultBoxName = 'restaurant_platform_storage';

  /// Initializes Hive and opens the default box.
  static Future<LocalStorageService> init({
    String boxName = _defaultBoxName,
  }) async {
    await Hive.initFlutter();
    final box = await Hive.openBox<dynamic>(boxName);
    return LocalStorageService(box);
  }

  /// Write a value to storage.
  Future<void> write<T>(String key, T value) async {
    await _box.put(key, value);
  }

  /// Read a value from storage.
  T? read<T>(String key) {
    return _box.get(key) as T?;
  }

  /// Read a value from storage, returning a default value if not found.
  T readWithDefault<T>(String key, T defaultValue) {
    return _box.get(key, defaultValue: defaultValue) as T;
  }

  /// Delete a value from storage.
  Future<void> delete(String key) async {
    await _box.delete(key);
  }

  /// Check if a key exists in storage.
  bool contains(String key) {
    return _box.containsKey(key);
  }

  /// Clear all entries in the box.
  Future<void> clear() async {
    await _box.clear();
  }

  /// Close the box.
  Future<void> close() async {
    await _box.close();
  }
}

/// Riverpod provider for the [LocalStorageService].
/// Must be overridden in the main app entrypoint after initialization.
final localStorageServiceProvider = Provider<LocalStorageService>((ref) {
  throw UnimplementedError('localStorageServiceProvider must be overridden');
});
