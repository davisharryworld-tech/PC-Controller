import 'package:flutter/material.dart';
import 'screens/dashboard_screen.dart';
import 'services/pc_service.dart';
import 'services/voice_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize background PC controller socket & voice recognition
  final pcService = PCService();
  await pcService.init();

  final voiceService = VoiceService();
  await voiceService.initialize();

  runApp(const PCControllerApp());
}

class PCControllerApp extends StatelessWidget {
  const PCControllerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PC Controller',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF090D16),
        primaryColor: const Color(0xFF6366F1),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF6366F1),
          secondary: Color(0xFF38BDF8),
          surface: Color(0xFF131C2E),
        ),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
    );
  }
}
