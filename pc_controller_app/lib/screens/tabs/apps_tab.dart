import 'package:flutter/material.dart';
import '../../services/pc_service.dart';

class AppsTab extends StatefulWidget {
  const AppsTab({super.key});

  @override
  State<AppsTab> createState() => _AppsTabState();
}

class _AppsTabState extends State<AppsTab> {
  final TextEditingController _urlCtrl = TextEditingController();
  final TextEditingController _progCtrl = TextEditingController();
  final PCService _pc = PCService();

  @override
  void dispose() {
    _urlCtrl.dispose();
    _progCtrl.dispose();
    super.dispose();
  }

  void _openUrl() {
    final u = _urlCtrl.text.trim();
    if (u.isNotEmpty) {
      _pc.sendAction('open_url', {'url': u});
      _urlCtrl.clear();
    }
  }

  void _runProgram() {
    final p = _progCtrl.text.trim();
    if (p.isNotEmpty) {
      _pc.sendAction('run_program', {'program': p});
      _progCtrl.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // App Grid
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF1E293B)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '🚀 Popular Apps & Websites',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: 2.3,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
                children: [
                  _appTile('🤖 ChatGPT', const Color(0xFF10B981), () => _pc.sendCommand('open chat gpt')),
                  _appTile('▶️ YouTube', const Color(0xFFEF4444), () => _pc.sendCommand('open youtube')),
                  _appTile('💬 WhatsApp', const Color(0xFF25D366), () => _pc.sendCommand('open whatsapp')),
                  _appTile('🌐 Chrome', const Color(0xFF3B82F6), () => _pc.sendCommand('open chrome')),
                  _appTile('✉️ Gmail', const Color(0xFFEA4335), () => _pc.sendAction('open_gmail')),
                  _appTile('📝 Notepad', const Color(0xFF8B5CF6), () => _pc.sendAction('open_notepad')),
                  _appTile('🔢 Calculator', const Color(0xFFF59E0B), () => _pc.sendAction('open_calc')),
                  _appTile('🐙 GitHub', const Color(0xFF64748B), () => _pc.sendAction('open_github')),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Custom URL Launcher
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF1E293B)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '🌐 Open Custom Website / URL',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _urlCtrl,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: InputDecoration(
                        hintText: 'e.g. facebook.com, twitter.com...',
                        hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                        filled: true,
                        fillColor: const Color(0xFF090D16),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onSubmitted: (_) => _openUrl(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _openUrl,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF6366F1),
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Open', style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Custom Program Launcher
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF1E293B)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '💻 Run Custom Program / Command',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _progCtrl,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: InputDecoration(
                        hintText: 'e.g. mspaint, cmd, taskmgr...',
                        hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                        filled: true,
                        fillColor: const Color(0xFF090D16),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onSubmitted: (_) => _runProgram(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _runProgram,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF38BDF8),
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Run', style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _appTile(String title, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF090D16),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        alignment: Alignment.centerLeft,
        child: Text(
          title,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}

