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
  final TextEditingController _typeController = TextEditingController();
  bool _isLiveMirroring = false;
  Uint8List? _liveFrameBytes;
  Uint8List? _screenshotBytes;
  bool _isLoading = false;
  bool _isFetchingFrame = false;
  bool _isExpanded = false;
  Timer? _streamTimer;

  @override
  void dispose() {
    _typeController.dispose();
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
    // 45ms interval = ~22 FPS ultra-low-latency PC screen preview
    _streamTimer = Timer.periodic(const Duration(milliseconds: 45), (_) async {
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
                        ? GestureDetector(
                            onPanUpdate: (details) {
                              _pc.sendMouseMove(
                                (details.delta.dx * 2.2).toInt(),
                                (details.delta.dy * 2.2).toInt(),
                              );
                            },
                            onTap: () => _pc.sendAction('mouse_click', {'button': 'left'}),
                            onDoubleTap: () => _pc.sendAction('mouse_click', {'button': 'right'}),
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

              // Integrated Mouse Control Section directly on Live Screen
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF090D18),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF1E293B)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '🖱️ Screen Mouse Controller',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFFC7D2FE)),
                        ),
                        Text(
                          'Trackpad & Clicks',
                          style: TextStyle(fontSize: 10, color: Colors.grey),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // Touchpad Surface (High-speed 3.8x with zero lag)
                    GestureDetector(
                      onPanUpdate: (details) {
                        _pc.sendMouseMove(
                          (details.delta.dx * 3.8).toInt(),
                          (details.delta.dy * 3.8).toInt(),
                        );
                      },
                      onTap: () => _pc.sendAction('mouse_click', {'button': 'left'}),
                      onDoubleTap: () => _pc.sendAction('mouse_click', {'button': 'right'}),
                      child: Container(
                        height: 90,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: const Color(0xFF0D1527),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0x804F46E5)),
                        ),
                        child: const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text('👆 Fast Gliding Touchpad', style: TextStyle(color: Color(0xFFA5B4FC), fontWeight: FontWeight.bold, fontSize: 12)),
                              SizedBox(height: 2),
                              Text('Drag to move mouse • 1-Tap: Left • 2-Tap: Right', style: TextStyle(color: Colors.grey, fontSize: 10)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // PC Live Typing Box
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF090D18),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF1E293B)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '⌨️ Live Typing Box',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFFC7D2FE)),
                        ),
                        Text(
                          'Direct Cursor Typing',
                          style: TextStyle(fontSize: 10, color: Colors.grey),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _typeController,
                            style: const TextStyle(color: Colors.white, fontSize: 13),
                            decoration: InputDecoration(
                              hintText: 'Yahan type karein aur Type dabayein...',
                              hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                              filled: true,
                              fillColor: const Color(0xFF0B1120),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF1E293B))),
                              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF1E293B))),
                              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF6366F1))),
                            ),
                            onSubmitted: (txt) {
                              if (txt.isNotEmpty) {
                                _pc.sendAction('type_text', {'text': txt});
                                _typeController.clear();
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed: () {
                            final txt = _typeController.text;
                            if (txt.isNotEmpty) {
                              _pc.sendAction('type_text', {'text': txt});
                              _typeController.clear();
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF6366F1),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          child: const Text('Type 🚀', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _pc.sendAction('press_key', {'key': 'enter'}),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: Color(0xFF334155)),
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                            ),
                            child: const Text('⏎ Enter', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _pc.sendAction('press_key', {'key': 'backspace'}),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: Color(0xFF334155)),
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                            ),
                            child: const Text('⌫ Backspace', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _pc.sendAction('press_key', {'key': 'space'}),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: Color(0xFF334155)),
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                            ),
                            child: const Text('␣ Space', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Small Compact Capture & Download Screenshot Button
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: _isLoading ? null : _captureScreenshot,
                  icon: _isLoading
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.camera_rounded, size: 16),
                  label: Text(_isLoading ? 'Capturing...' : '📸 Capture Screen & Direct Download'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.grey.shade300,
                    side: const BorderSide(color: Color(0xFF334155)),
                    padding: const EdgeInsets.symmetric(vertical: 11),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ),
              if (_screenshotBytes != null) ...[
                const SizedBox(height: 10),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
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
