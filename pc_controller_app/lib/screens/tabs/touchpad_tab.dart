import 'package:flutter/material.dart';
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
                  border: Border.all(color: const Color(0xFF1E293B)),
                ),
                child: Center(
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

