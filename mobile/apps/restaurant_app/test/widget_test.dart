import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:restaurant_app/features/dashboard/dashboard_screen.dart';

void main() {
  testWidgets('DashboardScreen shows title and description', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: DashboardScreen()),
    );

    expect(find.text('Restaurant Dashboard'), findsOneWidget);
    expect(find.text('Manage orders, menus, and staff.'), findsOneWidget);
    expect(find.byIcon(Icons.dashboard_outlined), findsOneWidget);
  });
}
