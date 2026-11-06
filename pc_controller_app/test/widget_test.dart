import 'package:flutter_test/flutter_test.dart';
import 'package:pc_controller_app/main.dart';

void main() {
  testWidgets('App basic smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const PCControllerApp());
    expect(find.byType(PCControllerApp), findsOneWidget);
  });
}
