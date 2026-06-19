import 'package:delivery_app/features/home/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('HomeScreen shows title and description', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: HomeScreen()),
    );

    expect(find.text('Delivery Home'), findsOneWidget);
    expect(
      find.text('Go online to start receiving deliveries.'),
      findsOneWidget,
    );
    expect(find.byIcon(Icons.delivery_dining_outlined), findsOneWidget);
  });
}
