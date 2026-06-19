import 'dart:async';
import 'package:core/core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:networking/networking.dart';
import 'package:storage/storage.dart';

/// Repository for authentication requests.
class AuthRepository {
  AuthRepository(this._dioClient, this._storage);

  final DioClient _dioClient;
  final LocalStorageService _storage;

  /// Perform login and save response tokens.
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dioClient.post<dynamic>(
        '/api/v1/auth/login',
        data: {'email': email, 'password': password},
      );

      final envelope = response.data as Map<String, dynamic>;
      final data = envelope['data'] as Map<String, dynamic>;

      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String;

      await _storage.write('access_token', accessToken);
      await _storage.write('refresh_token', refreshToken);

      return data;
    } catch (e) {
      rethrow;
    }
  }

  /// Perform registration.
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String phoneNumber,
    required List<String> roles,
  }) async {
    try {
      final response = await _dioClient.post<dynamic>(
        '/api/v1/auth/register',
        data: {
          'email': email,
          'password': password,
          'phone_number': phoneNumber,
          'roles': roles,
        },
      );
      final envelope = response.data as Map<String, dynamic>;
      return envelope['data'] as Map<String, dynamic>;
    } catch (e) {
      rethrow;
    }
  }

  /// Fetch profile of current user.
  Future<Map<String, dynamic>> getProfile() async {
    try {
      final response = await _dioClient.get<dynamic>('/api/v1/me');
      final envelope = response.data as Map<String, dynamic>;
      return envelope['data'] as Map<String, dynamic>;
    } catch (e) {
      rethrow;
    }
  }

  /// Clear authentication tokens from storage.
  Future<void> logout() async {
    await _storage.delete('access_token');
    await _storage.delete('refresh_token');
  }
}

/// Authentication state model.
class AuthState {
  const AuthState({
    this.isAuthenticated = false,
    this.userProfile,
    this.errorMessage,
    this.isLoading = false,
  });

  final bool isAuthenticated;
  final Map<String, dynamic>? userProfile;
  final String? errorMessage;
  final bool isLoading;

  AuthState copyWith({
    bool? isAuthenticated,
    Map<String, dynamic>? userProfile,
    String? errorMessage,
    bool? isLoading,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      userProfile: userProfile ?? this.userProfile,
      errorMessage: errorMessage ?? this.errorMessage,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

/// Notifier that manages authentication state.
class AuthNotifier extends Notifier<AuthState> {
  late final AuthRepository _repository;
  late final LocalStorageService _storage;

  @override
  AuthState build() {
    _storage = ref.watch(localStorageServiceProvider);
    final dioClient = ref.watch(dioClientProvider);
    _repository = AuthRepository(dioClient, _storage);

    final token = _storage.read<String>('access_token');
    if (token != null) {
      unawaited(_fetchProfile());
      return const AuthState(isAuthenticated: true);
    }
    return const AuthState();
  }

  Future<void> _fetchProfile() async {
    try {
      final profile = await _repository.getProfile();
      state = state.copyWith(userProfile: profile, isAuthenticated: true);
    } on Exception catch (e) {
      AppLogger.error('Failed to fetch user profile', e);
      if (e is AuthenticationException) {
        await logout();
      }
    }
  }

  /// Perform login action.
  Future<void> login(String email, String password) async {
    state = AuthState(
      isLoading: true,
      isAuthenticated: state.isAuthenticated,
      userProfile: state.userProfile,
    );
    try {
      await _repository.login(email, password);
      state = state.copyWith(isAuthenticated: true, isLoading: false);
      await _fetchProfile();
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// Perform registration action.
  Future<void> register({
    required String email,
    required String password,
    required String phoneNumber,
    required List<String> roles,
  }) async {
    state = AuthState(
      isLoading: true,
      isAuthenticated: state.isAuthenticated,
      userProfile: state.userProfile,
    );
    try {
      await _repository.register(
        email: email,
        password: password,
        phoneNumber: phoneNumber,
        roles: roles,
      );
      state = state.copyWith(isLoading: false);
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// Perform logout action.
  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    try {
      await _repository.logout();
      state = const AuthState();
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }
}

/// Provider for AuthRepository.
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  final storage = ref.watch(localStorageServiceProvider);
  return AuthRepository(dioClient, storage);
});

/// Riverpod state provider for authentication.
final authStateProvider = NotifierProvider<AuthNotifier, AuthState>(() {
  return AuthNotifier();
});
