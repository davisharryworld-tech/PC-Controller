import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../services/pc_service.dart';

class ScreenTab extends StatefulWidget {
  const ScreenTab({super.key});

  @override
  State<ScreenTab> createState() => _ScreenTabState();
}

class _ScreenTabState extends State<ScreenTab> {
  final PCService _pc = PCService();
  bool _isLiveMirroring = false;
  Uint8List? _screenshotBytes;
  bool _isLoading = false;
  int _streamKey = 0;

  Future<void> _captureScreenshot() async {
    setState(() => _isLoading = true);
    try {
      final res = await http.get(Uri.parse('${_pc.screenshotUrl}?t=${DateTime.now().millisecondsSinceEpoch}'));
      if (res.statusCode == 200) {
        setState(() {
          _screenshotBytes = res.bodyBytes;
          _isLoading = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('📸 PC Screenshot captured!'), backgroundColor: Color(0xFF10B981)),
          );
        }
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _toggleLiveMirror() {
    setState(() {
      _isLiveMirroring = !_isLiveMirroring;
      _streamKey++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Live Screen Mirror Card
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
              Row(
                children: [
                  const Icon(Icons.screen_share_rounded, color: Color(0xFF6366F1), size: 20),
                  const SizedBox(width: 8),
                  const Text(
                    '📺 Live PC Screen Mirror',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const Spacer(),
                  Switch(
                    value: _isLiveMirroring,
                    activeThumbColor: const Color(0xFF10B981),
                    onChanged: (val) => _toggleLiveMirror(),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'PC ki screen mobile par live dekhein. Low-latency stream active.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 12),

              // Screen Viewer
              Container(
                width: double.infinity,
                height: 220,
                decoration: BoxDecoration(
                  color: const Color(0xFF070B14),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF1E293B)),
                ),
                clipBehavior: Clip.antiAlias,
                child: _isLiveMirroring
                    ? Image.network(
                        '${_pc.screenStreamUrl}?k=$_streamKey',
                        fit: BoxFit.contain,
                        gaplessPlayback: true,
                        errorBuilder: (context, error, stackTrace) => Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.videocam_off_rounded, color: Colors.grey, size: 36),
                              const SizedBox(height: 8),
                              Text('Connecting to PC Screen Stream...', style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
                            ],
                          ),
                        ),
                      )
                    : Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.tv_rounded, size: 48, color: Colors.grey.shade700),
                            const SizedBox(height: 8),
                            Text('Live Mirror is OFF', style: TextStyle(color: Colors.grey.shade500, fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 4),
                            Text('Upar switch ON karein live screen dekhne ke liye', style: TextStyle(color: Colors.grey.shade600, fontSize: 11)),
                          ],
                        ),
                      ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Instant Screenshot Card
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
              Row(
                children: [
                  const Icon(Icons.camera_alt_rounded, color: Color(0xFF38BDF8), size: 20),
                  const SizedBox(width: 8),
                  const Text(
                    '📸 Instant PC Screenshot',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'PC ka 1-Tap high-definition screenshot khinchein.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _captureScreenshot,
                  icon: _isLoading
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.camera_rounded, size: 18),
                  label: Text(_isLoading ? 'Capturing...' : 'Capture Screenshot Now'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0284C7),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              if (_screenshotBytes != null) ...[
                const SizedBox(height: 14),
                Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFF38BDF8)),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Image.memory(_screenshotBytes!, fit: BoxFit.contain),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}
