import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../services/pc_service.dart';

class TouchpadTab extends StatefulWidget {
  const TouchpadTab({super.key});

  @override
  State<TouchpadTab> createState() => _TouchpadTabState();
}

class _TouchpadTabState extends State<TouchpadTab> {
  final PCService _pc = PCService();

  double _accumX = 0;
  double _accumY = 0;
  DateTime _lastMoveTime = DateTime.now();

  bool _showScreen = false;
  Timer? _screenTimer;
  Uint8List? _screenFrame;
  bool _isFetching = false;

  @override
  void dispose() {
    _screenTimer?.cancel();
    super.dispose();
  }

  void _toggleScreen() {
    setState(() => _showScreen = !_showScreen);
    if (_showScreen) {
      _screenTimer?.cancel();
      _screenTimer = Timer.periodic(const Duration(milliseconds: 130), (_) async {
        if (!_showScreen || _isFetching) return;
        _isFetching = true;
        try {
          final res = await http.get(
            Uri.parse('${_pc.screenshotUrl}&t=${DateTime.now().millisecondsSinceEpoch}'),
            headers: _pc.authHeaders,
          ).timeout(const Duration(seconds: 2));
          if (res.statusCode == 200 && mounted && _showScreen) {
            setState(() => _screenFrame = res.bodyBytes);
          }
        } catch (_) {} finally {
          _isFetching = false;
        }
      });
    } else {
      _screenTimer?.cancel();
    }
  }

  void _onPanUpdate(DragUpdateDetails details) {
    _accumX += details.delta.dx;
    _accumY += details.delta.dy;

    final now = DateTime.now();
    if (now.difference(_lastMoveTime).inMilliseconds > 30) {
      _lastMoveTime = now;
      final sendDx = (_accumX * 2.2).round();
      final sendDy = (_accumY * 2.2).round();
      _accumX = 0;
      _accumY = 0;

      if (sendDx != 0 || sendDy != 0) {
        _pc.sendMouseMove(sendDx, sendDy);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          // Screen preview toggle bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '🖱️ Touchpad Surface',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey.shade300, fontSize: 13),
              ),
              InkWell(
                onTap: _toggleScreen,
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: _showScreen ? const Color(0xFF10B981).withValues(alpha: 0.15) : const Color(0xFF131C2E),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: _showScreen ? const Color(0xFF10B981) : const Color(0xFF334155)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _showScreen ? Icons.tv_rounded : Icons.tv_off_rounded,
                        size: 15,
                        color: _showScreen ? const Color(0xFF10B981) : Colors.grey.shade400,
                      ),
                      const SizedBox(width: 5),
                      Text(
                        _showScreen ? 'Live Screen: ON' : 'Show Screen',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: _showScreen ? const Color(0xFF10B981) : Colors.grey.shade400,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Touchpad Surface
          Expanded(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onPanUpdate: _onPanUpdate,
              onTap: () => _pc.sendAction('mouse_click', {'button': 'left'}),
              onDoubleTap: () => _pc.sendAction('mouse_click', {'button': 'right'}),
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: const Color(0xFF090D16),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: _showScreen ? const Color(0xFF6366F1) : const Color(0xFF1E293B)),
                ),
                clipBehavior: Clip.antiAlias,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    if (_showScreen && _screenFrame != null)
                      Image.memory(
                        _screenFrame!,
                        fit: BoxFit.contain,
                        gaplessPlayback: true,
                      ),
                    if (!_showScreen || _screenFrame == null)
                      Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.touch_app_rounded, size: 48, color: Colors.grey.shade600),
                            const SizedBox(height: 10),
                            Text(
                              'Virtual Touchpad',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.grey.shade400,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Ungli ghumayein mouse chalane ke liye.\nTap: Left Click • Double Tap: Right Click',
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Scroll Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendAction('mouse_scroll', {'amount': 300}),
                  icon: const Icon(Icons.arrow_upward_rounded, size: 16),
                  label: const Text('Scroll Up'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF131C2E),
                    foregroundColor: const Color(0xFF38BDF8),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendAction('mouse_scroll', {'amount': -300}),
                  icon: const Icon(Icons.arrow_downward_rounded, size: 16),
                  label: const Text('Scroll Down'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF131C2E),
                    foregroundColor: const Color(0xFF38BDF8),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Left Click Button only
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => _pc.sendAction('mouse_click', {'button': 'left'}),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6366F1),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: const Text('Left Click', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }
}

