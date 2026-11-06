import 'package:flutter/material.dart';
import '../services/pc_service.dart';

class SettingsDialog extends StatefulWidget {
  const SettingsDialog({super.key});

  @override
  State<SettingsDialog> createState() => _SettingsDialogState();
}

class _SettingsDialogState extends State<SettingsDialog> {
  final PCService _pc = PCService();
  late TextEditingController _hostCtrl;
  late TextEditingController _portCtrl;
  late TextEditingController _tailscaleCtrl;
  late bool _useTailscale;

  @override
  void initState() {
    super.initState();
    _hostCtrl = TextEditingController(text: _pc.activeHost);
    _portCtrl = TextEditingController(text: _pc.port.toString());
    _tailscaleCtrl = TextEditingController(text: '100.70.0.109');
    _useTailscale = _pc.useTailscale;
  }

  @override
  void dispose() {
    _hostCtrl.dispose();
    _portCtrl.dispose();
    _tailscaleCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF131C2E),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: const Row(
        children: [
          Icon(Icons.settings_rounded, color: Color(0xFF6366F1), size: 22),
          SizedBox(width: 8),
          Text('PC Connection Settings', style: TextStyle(color: Colors.white, fontSize: 16)),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Mode selector
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: const Color(0xFF090D16),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: ChoiceChip(
                      label: const Text('📶 Local Wi-Fi'),
                      selected: !_useTailscale,
                      selectedColor: const Color(0xFF6366F1),
                      labelStyle: TextStyle(
                        color: !_useTailscale ? Colors.white : Colors.grey,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                      onSelected: (val) {
                        setState(() {
                          _useTailscale = !val ? true : false;
                          _hostCtrl.text = '10.168.124.10';
                        });
                      },
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: ChoiceChip(
                      label: const Text('🔒 Tailscale'),
                      selected: _useTailscale,
                      selectedColor: const Color(0xFF818CF8),
                      labelStyle: TextStyle(
                        color: _useTailscale ? Colors.white : Colors.grey,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                      onSelected: (val) {
                        setState(() {
                          _useTailscale = val;
                          _hostCtrl.text = '100.70.0.109';
                        });
                      },
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // IP field
            TextField(
              controller: _hostCtrl,
              style: const TextStyle(color: Colors.white, fontSize: 13),
              decoration: const InputDecoration(
                labelText: 'PC IP Address',
                labelStyle: TextStyle(color: Colors.grey, fontSize: 12),
                filled: true,
                fillColor: Color(0xFF090D16),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),

            // Port field
            TextField(
              controller: _portCtrl,
              keyboardType: TextInputType.number,
              style: const TextStyle(color: Colors.white, fontSize: 13),
              decoration: const InputDecoration(
                labelText: 'Port (Default: 8000)',
                labelStyle: TextStyle(color: Colors.grey, fontSize: 12),
                filled: true,
                fillColor: Color(0xFF090D16),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),

            Text(
              _useTailscale
                  ? '🔒 Tailscale Remote VPN Mode active: Anywhere internet connection.'
                  : '📶 Local Wi-Fi Network Mode active: Ensure phone and PC are on same router.',
              style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF6366F1),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          ),
          onPressed: () async {
            final h = _hostCtrl.text.trim();
            final p = int.tryParse(_portCtrl.text.trim()) ?? 8000;
            await _pc.updateConfig(
              host: _useTailscale ? '10.168.124.10' : h,
              port: p,
              tailscaleIp: _useTailscale ? h : '100.70.0.109',
              useTailscale: _useTailscale,
            );
            if (!mounted) return;
            Navigator.pop(context);
          },
          child: const Text('Save & Connect', style: TextStyle(color: Colors.white)),
        ),
      ],
    );
  }
}
