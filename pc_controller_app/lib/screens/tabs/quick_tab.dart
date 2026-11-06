import 'package:flutter/material.dart';
import '../../services/pc_service.dart';

class QuickTab extends StatelessWidget {
  const QuickTab({super.key});

  @override
  Widget build(BuildContext context) {
    final pc = PCService();

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Volume Control Card
        _buildCard(
          title: '🔊 Audio & Volume Control',
          subtitle: 'Adjust master system volume on your Windows PC',
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.volume_up_rounded,
                    label: 'Volume +10%',
                    color: const Color(0xFF6366F1),
                    onTap: () => pc.sendAction('volume_up'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.volume_down_rounded,
                    label: 'Volume -10%',
                    color: const Color(0xFF3B82F6),
                    onTap: () => pc.sendAction('volume_down'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.volume_off_rounded,
                    label: 'Mute / Unmute',
                    color: const Color(0xFFEAB308),
                    onTap: () => pc.sendAction('volume_mute'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.notifications_active_rounded,
                    label: 'Test Beep',
                    color: const Color(0xFF10B981),
                    onTap: () => pc.sendAction('beep'),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Media Control Card
        _buildCard(
          title: '🎵 Media & YouTube Playback',
          subtitle: 'Control videos and music playing on the PC',
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.skip_previous_rounded,
                    label: 'Previous',
                    color: const Color(0xFF1E293B),
                    onTap: () => pc.sendAction('media_prev'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.play_arrow_rounded,
                    label: 'Play / Pause',
                    color: const Color(0xFF6366F1),
                    onTap: () => pc.sendAction('media_play_pause'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.skip_next_rounded,
                    label: 'Next',
                    color: const Color(0xFF1E293B),
                    onTap: () => pc.sendAction('media_next'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            _buildButton(
              icon: Icons.video_library_rounded,
              label: '▶️ Click & Play YouTube First Video',
              color: const Color(0xFFEF4444),
              onTap: () => pc.sendCommand('play karo is song ko'),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // 1-Tap Quick Workflows / Macros Card
        _buildCard(
          title: '⚡ 1-Tap Quick Workflows (Macros)',
          subtitle: 'Aik tap me multiple software aur settings chalayein',
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.work_rounded,
                    label: '💼 Work Mode',
                    color: const Color(0xFF6366F1),
                    onTap: () => pc.sendAction('macro_work_mode'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.sports_esports_rounded,
                    label: '🎮 Gaming Mode',
                    color: const Color(0xFF8B5CF6),
                    onTap: () => pc.sendAction('macro_gaming_mode'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.menu_book_rounded,
                    label: '📚 Study Mode',
                    color: const Color(0xFF059669),
                    onTap: () => pc.sendAction('macro_study_mode'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.coffee_rounded,
                    label: '☕ Chill Mode',
                    color: const Color(0xFFD97706),
                    onTap: () => pc.sendAction('macro_chill_mode'),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Remote Power & Wake-on-LAN Card
        _buildCard(
          title: '⚡ Power Controls & Wake-on-LAN',
          subtitle: 'Sleep, restart ya band PC ko remote signal se on karein',
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildButton(
                    icon: Icons.bedtime_rounded,
                    label: 'Sleep PC',
                    color: const Color(0xFF1E293B),
                    onTap: () => pc.sendAction('system_sleep'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildButton(
                    icon: Icons.restart_alt_rounded,
                    label: 'Restart PC',
                    color: const Color(0xFFD97706),
                    onTap: () => pc.sendAction('system_restart'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () async {
                  final wolInfo = await pc.fetchWolInfo();
                  final macs = wolInfo['mac_addresses'] as List<dynamic>? ?? [];
                  String targetMac = '50-9A-4C-51-28-8B';
                  if (macs.isNotEmpty) {
                    targetMac = macs.first['mac']?.toString() ?? targetMac;
                  }
                  final sent = await pc.sendWakeOnLan(targetMac);
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(sent ? '⚡ Magic Packet sent to PC ($targetMac)!' : 'WOL packet send failed'),
                        backgroundColor: const Color(0xFF10B981),
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.flash_on_rounded, color: Colors.yellow, size: 20),
                label: const Text('⚡ Turn ON PC (Wake-on-LAN Magic Packet)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  side: const BorderSide(color: Color(0xFFF59E0B), width: 1.5),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCard({
    required String title,
    required String subtitle,
    required List<Widget> children,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF131C2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            subtitle,
            style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }

  Widget _buildButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return ElevatedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18),
      label: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        elevation: 0,
      ),
    );
  }
}

