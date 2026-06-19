import 'package:core/core.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:storage/storage.dart';

/// Wrapped Dio HTTP client exposing standard HTTP methods with error mapping.
class DioClient {
  DioClient(this.dio);

  final Dio dio;

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await dio.patch<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  AppException _handleDioException(DioException e) {
    AppLogger.error('Dio error: ${e.message}', e, e.stackTrace);
    final response = e.response;
    if (response != null) {
      var message = 'Server returned error status ${response.statusCode}';
      if (response.data is Map<String, dynamic>) {
        final dataMap = response.data as Map<String, dynamic>;
        if (dataMap.containsKey('message')) {
          message = dataMap['message'].toString();
        } else if (dataMap.containsKey('detail')) {
          message = dataMap['detail'].toString();
        }
      }

      if (response.statusCode == 401) {
        return AuthenticationException(message, response.data);
      } else if (response.statusCode == 400 || response.statusCode == 422) {
        return ValidationException(message, response.data);
      } else if (response.statusCode! >= 500) {
        return ServerException(message, response.data);
      }
      return UnknownException(message, response.data);
    }

    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.connectionError) {
      return const NetworkException(
        'Connection to server failed. Please check your internet connection.',
      );
    }
    return UnknownException(
      e.message ?? 'An unexpected network error occurred',
    );
  }
}

/// Interceptor that attaches JWT token and handles automatic refresh on 401.
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._storage, this._refreshDio);

  final LocalStorageService _storage;
  final Dio _refreshDio;
  bool _isRefreshing = false;
  final List<MapEntry<RequestOptions, ErrorInterceptorHandler>> _requestQueue =
      [];

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = _storage.read<String>('access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return super.onRequest(options, handler);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      final options = err.requestOptions;
      final isRetried = options.extra['retried'] == true;
      final isAuthPath =
          options.path.contains('/auth/refresh') ||
          options.path.contains('/auth/login');
      if (isRetried || isAuthPath) {
        return super.onError(err, handler);
      }

      final refreshToken = _storage.read<String>('refresh_token');
      if (refreshToken == null) {
        return super.onError(err, handler);
      }

      if (_isRefreshing) {
        _requestQueue.add(MapEntry(options, handler));
        return;
      }

      _isRefreshing = true;
      options.extra['retried'] = true;

      try {
        AppLogger.info('Attempting token refresh');
        final response = await _refreshDio.post<dynamic>(
          '/api/v1/auth/refresh',
          data: {'refresh_token': refreshToken},
        );

        if (response.statusCode == 200 && response.data != null) {
          final envelope = response.data as Map<String, dynamic>;
          final data = envelope['data'] as Map<String, dynamic>;
          final newAccessToken = data['access_token'] as String;
          final newRefreshToken = data['refresh_token'] as String;

          await _storage.write('access_token', newAccessToken);
          await _storage.write('refresh_token', newRefreshToken);

          AppLogger.info('Token refresh successful');

          options.headers['Authorization'] = 'Bearer $newAccessToken';
          final cloneResponse = await _refreshDio.fetch<dynamic>(options);
          handler.resolve(cloneResponse);

          for (final entry in _requestQueue) {
            final queuedOptions = entry.key;
            queuedOptions.headers['Authorization'] = 'Bearer $newAccessToken';
            queuedOptions.extra['retried'] = true;
            try {
              final res = await _refreshDio.fetch<dynamic>(queuedOptions);
              entry.value.resolve(res);
            } on DioException catch (dioErr) {
              entry.value.next(dioErr);
            }
          }
          _requestQueue.clear();
        } else {
          await _handleLogout();
          handler.next(err);
        }
      } on Exception catch (e) {
        AppLogger.error('Token refresh failed', e);
        await _handleLogout();
        handler.next(err);
      } finally {
        _isRefreshing = false;
      }
      return;
    }

    return super.onError(err, handler);
  }

  Future<void> _handleLogout() async {
    await _storage.delete('access_token');
    await _storage.delete('refresh_token');
    _requestQueue.clear();
  }
}

/// Provider for the HTTP DioClient.
final dioClientProvider = Provider<DioClient>((ref) {
  final storage = ref.watch(localStorageServiceProvider);
  const baseUrl = 'http://localhost:8000';

  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  final refreshDio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  dio.interceptors.add(AuthInterceptor(storage, refreshDio));
  dio.interceptors.add(
    LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => AppLogger.debug(obj.toString()),
    ),
  );

  return DioClient(dio);
});
