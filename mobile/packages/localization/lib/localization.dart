import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Simple localizations delegate and helper class.
class AppLocalizations {
  AppLocalizations(this.locale);

  final Locale locale;

  /// Fetch localizations from the build context.
  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  /// App localization delegate instance.
  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  static final Map<String, Map<String, String>> _localizedValues = {
    'en': {
      'app_title': 'Restaurant Platform',
      'login': 'Login',
      'register': 'Register',
      'email': 'Email',
      'password': 'Password',
      'phone_number': 'Phone Number',
      'submit': 'Submit',
      'logout': 'Logout',
      'error': 'Error',
      'loading': 'Loading...',
    },
    'es': {
      'app_title': 'Plataforma de Restaurante',
      'login': 'Iniciar Sesión',
      'register': 'Registrarse',
      'email': 'Correo electrónico',
      'password': 'Contraseña',
      'phone_number': 'Número de teléfono',
      'submit': 'Enviar',
      'logout': 'Cerrar sesión',
      'error': 'Error',
      'loading': 'Cargando...',
    },
  };

  /// Translate a key.
  String translate(String key) {
    final langCode = locale.languageCode;
    return _localizedValues[langCode]?[key] ??
        _localizedValues['en']?[key] ??
        key;
  }
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['en', 'es'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(AppLocalizations(locale));
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

/// Helper extension to easily access localization.
extension AppLocalizationsX on BuildContext {
  /// Translate [key] based on the current context locale.
  String l10n(String key) {
    return AppLocalizations.of(this)?.translate(key) ?? key;
  }
}
