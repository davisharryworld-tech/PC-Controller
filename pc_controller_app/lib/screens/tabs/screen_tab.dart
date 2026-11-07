import 'dart:async';
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
  Uint8List? _liveFrameBytes;
  Uint8List? _screenshotBytes;
  bool _isLoading = false;
  bool _isFetchingFrame = false;
  bool _isExpanded = false;
  Timer? _streamTimer;

  @override
  void dispose() {
    _streamTimer?.cancel();
    super.dispose();
  }

  void _toggleLiveMirror() {
    setState(() {
      _isLiveMirroring = !_isLiveMirroring;
    });

    if (_isLiveMirroring) {
      _startStreamLoop();
    } else {
      _streamTimer?.cancel();
    }
  }

  void _startStreamLoop() {
    _streamTimer?.cancel();
    // 110ms interval = ~9 FPS smooth low-latency PC screen preview
    _streamTimer = Timer.periodic(const Duration(milliseconds: 110), (_) async {
      if (!_isLiveMirroring || _isFetchingFrame) return;
      _isFetchingFrame = true;
      try {
        final res = await http.get(
          Uri.parse('${_pc.screenshotUrl}&t=${DateTime.now().millisecondsSinceEpoch}'),
          headers: _pc.authHeaders,
        ).timeout(const Duration(seconds: 2));

        if (res.statusCode == 200 && mounted && _isLiveMirroring) {
          setState(() {
            _liveFrameBytes = res.bodyBytes;
          });
        }
      } catch (_) {} finally {
        _isFetchingFrame = false;
      }
    });
  }

  Future<void> _captureScreenshot() async {
    setState(() => _isLoading = true);
    try {
      final res = await http.get(
        Uri.parse('${_pc.screenshotUrl}&raw=true&t=${DateTime.now().millisecondsSinceEpoch}'),
        headers: _pc.authHeaders,
      );
      if (res.statusCode == 200) {
        setState(() {
          _screenshotBytes = res.bodyBytes;
          _isLoading = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('📸 PC High-Def Screenshot captured!'), backgroundColor: Color(0xFF10B981)),
          );
        }
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
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
                  const Icon(Icons.screen_share_rounded, color: Color(0xFF6366F1), size: 22),
                  const SizedBox(width: 8),
                  const Text(
                    '📺 Live PC Screen Mirror',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
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
                'PC ki screen mobile par live dekhein. Red pointer = Mouse cursor.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 12),

              // Controls Bar (Expand & Refresh)
              if (_isLiveMirroring) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton.icon(
                      onPressed: () => setState(() => _isExpanded = !_isExpanded),
                      icon: Icon(_isExpanded ? Icons.fullscreen_exit_rounded : Icons.fullscreen_rounded, size: 18),
                      label: Text(_isExpanded ? 'Normal View' : 'Bari Screen'),
                      style: TextButton.styleFrom(
                        foregroundColor: const Color(0xFF818CF8),
                        visualDensity: VisualDensity.compact,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
              ],

              // Screen Viewer Box
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: double.infinity,
                height: _isExpanded ? 380 : 230,
                decoration: BoxDecoration(
                  color: const Color(0xFF070B14),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _isLiveMirroring ? const Color(0xFF6366F1) : const Color(0xFF1E293B), width: 1.5),
                ),
                clipBehavior: Clip.antiAlias,
                child: _isLiveMirroring
                    ? (_liveFrameBytes != null
                        ? InteractiveViewer(
                            panEnabled: true,
                            scaleEnabled: true,
                            minScale: 1.0,
                            maxScale: 3.5,
                            child: Image.memory(
                              _liveFrameBytes!,
                              fit: BoxFit.contain,
                              gaplessPlayback: true,
                            ),
                          )
                        : const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                SizedBox(width: 28, height: 28, child: CircularProgressIndicator(strokeWidth: 2.5, color: Color(0xFF6366F1))),
                                SizedBox(height: 12),
                                Text('Connecting live PC display...', style: TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ))
                    : Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.tv_rounded, size: 52, color: Colors.grey.shade700),
                            const SizedBox(height: 8),
                            const Text('Live Screen Band Hai', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold, fontSize: 14)),
                            const SizedBox(height: 4),
                            Text('Upar switch ON karein PC screen dekhne k liye', style: TextStyle(color: Colors.grey.shade600, fontSize: 11)),
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
              const Row(
                children: [
                  Icon(Icons.camera_alt_rounded, color: Color(0xFF38BDF8), size: 20),
                  SizedBox(width: 8),
                  Text(
                    '📸 Instant PC Screenshot',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'PC ka 1-Tap high-definition snapshot khinchein.',
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
                  label: Text(_isLoading ? 'Kheencha ja raha hai...' : '📸 Capture Screenshot Now'),
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
