import 'package:flutter/material.dart';
import '../services/pc_service.dart';
import '../widgets/voice_control_bar.dart';
import 'settings_dialog.dart';
import 'tabs/quick_tab.dart';
import 'tabs/touchpad_tab.dart';
import 'tabs/keyboard_tab.dart';
import 'tabs/screen_tab.dart';
import 'tabs/media_remote_tab.dart';
import 'tabs/files_clipboard_tab.dart';
import 'tabs/presentation_tab.dart';
import 'tabs/apps_tab.dart';
import 'tabs/running_apps_tab.dart';
import 'tabs/whatsapp_tab.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final PCService _pc = PCService();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 10, vsync: this);

    // Listen to PC result messages and display quick snackbar
    _pc.lastMessageNotifier.addListener(_showResultSnackbar);
  }

  @override
  void dispose() {
    _pc.lastMessageNotifier.removeListener(_showResultSnackbar);
    _tabController.dispose();
    super.dispose();
  }

  void _showResultSnackbar() {
    final msg = _pc.lastMessageNotifier.value;
    if (msg.isNotEmpty && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(msg),
          duration: const Duration(seconds: 2),
          backgroundColor: const Color(0xFF1E293B),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF090D16),
      appBar: AppBar(
        backgroundColor: const Color(0xFF131C2E),
        elevation: 0,
        title: Row(
          children: [
            const Text(
              '🎮 PC Controller',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const Spacer(),

            // Connection Status Badge
            ValueListenableBuilder<ConnectionStatus>(
              valueListenable: _pc.statusNotifier,
              builder: (context, status, _) {
                final isConnected = status == ConnectionStatus.connected;
                final isConnecting = status == ConnectionStatus.connecting;

                Color badgeColor = isConnected
                    ? const Color(0xFF10B981)
                    : isConnecting
                        ? const Color(0xFFF59E0B)
                        : const Color(0xFFEF4444);

                String label = isConnected
                    ? 'Connected'
                    : isConnecting
                        ? 'Connecting...'
                        : 'Offline';

                return InkWell(
                  onTap: () {
                    if (!isConnected) {
                      _pc.connect();
                    }
                  },
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: badgeColor.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: badgeColor.withOpacity(0.6)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: badgeColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          label,
                          style: TextStyle(
                            color: badgeColor,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Colors.white),
            tooltip: 'Connection Settings',
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => const SettingsDialog(),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Voice Control & Command Bar
            const Padding(
              padding: EdgeInsets.fromLTRB(12, 10, 12, 0),
              child: VoiceControlBar(),
            ),
            const SizedBox(height: 8),

            // Tab Bar
            Container(
              color: const Color(0xFF131C2E),
              child: TabBar(
                controller: _tabController,
                isScrollable: true,
                indicatorColor: const Color(0xFF6366F1),
                indicatorWeight: 3,
                labelColor: const Color(0xFF6366F1),
                unselectedLabelColor: Colors.grey.shade400,
                labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                tabs: const [
                  Tab(icon: Icon(Icons.flash_on_rounded, size: 18), text: '⚡ Quick'),
                  Tab(icon: Icon(Icons.touch_app_rounded, size: 18), text: '🖱️ Mouse'),
                  Tab(icon: Icon(Icons.keyboard_alt_outlined, size: 18), text: '⌨️ Live Typing'),
                  Tab(icon: Icon(Icons.screen_share_rounded, size: 18), text: '📺 Screen'),
                  Tab(icon: Icon(Icons.smart_display_rounded, size: 18), text: '🎬 Media'),
                  Tab(icon: Icon(Icons.send_to_mobile_rounded, size: 18), text: '📁 Files & Clip'),
                  Tab(icon: Icon(Icons.slideshow_rounded, size: 18), text: '📊 Slides'),
                  Tab(icon: Icon(Icons.rocket_launch_rounded, size: 18), text: '🚀 Apps'),
                  Tab(icon: Icon(Icons.close_rounded, size: 18), text: '❌ Close Apps'),
                  Tab(icon: Icon(Icons.chat_bubble_outline_rounded, size: 18), text: '💬 WhatsApp'),
                ],
              ),
            ),

            // Tab Pages (Scroll locked so mouse dragging never accidentally slides tabs)
            Expanded(
              child: TabBarView(
                controller: _tabController,
                physics: const NeverScrollableScrollPhysics(),
                children: const [
                  QuickTab(),
                  TouchpadTab(),
                  KeyboardTab(),
                  ScreenTab(),
                  MediaRemoteTab(),
                  FilesClipboardTab(),
                  PresentationTab(),
                  AppsTab(),
                  RunningAppsTab(),
                  WhatsAppTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

