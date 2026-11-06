import 'package:flutter/material.dart';
import '../../services/pc_service.dart';

class KeyboardTab extends StatefulWidget {
  const KeyboardTab({super.key});

  @override
  State<KeyboardTab> createState() => _KeyboardTabState();
}

class _KeyboardTabState extends State<KeyboardTab> {
  final TextEditingController _textCtrl = TextEditingController();
  final PCService _pc = PCService();
  String _previousLiveText = '';
  bool _isLiveTyping = true;

  @override
  void dispose() {
    _textCtrl.dispose();
    super.dispose();
  }

  void _onLiveTextChanged(String currentText) {
    if (!_isLiveTyping) return;

    if (currentText.length > _previousLiveText.length) {
      // Characters added (typed / autocompleted / pasted)
      final added = currentText.substring(_previousLiveText.length);
      _pc.sendAction('type_live', {'text': added});
    } else if (currentText.length < _previousLiveText.length) {
      // Characters removed (Backspace)
      final diff = _previousLiveText.length - currentText.length;
      for (int i = 0; i < diff; i++) {
        _pc.sendAction('press_key', {'key': 'backspace'});
      }
    }
    _previousLiveText = currentText;
  }

  void _clearLiveInput() {
    setState(() {
      _previousLiveText = '';
      _textCtrl.clear();
    });
  }

  void _typeInNotepad() {
    final t = _textCtrl.text;
    if (t.isNotEmpty) {
      _pc.sendAction('type_in_notepad', {'text': t});
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Live Real-Time Typing Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.5), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.flash_on_rounded, color: Color(0xFF10B981), size: 18),
                  const SizedBox(width: 6),
                  const Text(
                    '⚡ Real-Time Live Typing',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
                    ),
                    child: const Text(
                      '● Live Active',
                      style: TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Mobile par jo bhi type karenge, wo foran PC active window par live likha jayega.',
                style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _textCtrl,
                maxLines: 3,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                onChanged: _onLiveTextChanged,
                decoration: InputDecoration(
                  hintText: 'Yahan type karna shuru karein (Urdu / English / Numbers)...',
                  hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  filled: true,
                  fillColor: const Color(0xFF090D16),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _clearLiveInput,
                      icon: const Icon(Icons.cleaning_services_rounded, size: 15),
                      label: const Text('Clear Mobile Box'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.grey.shade300,
                        side: const BorderSide(color: Color(0xFF334155)),
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _typeInNotepad,
                      icon: const Icon(Icons.note_alt_rounded, size: 15),
                      label: const Text('Open in Notepad'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF6366F1),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Special Keys Card
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
                '🎮 Special Keyboard Keys',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(child: _keyBtn('ENTER', () => _pc.sendAction('press_key', {'key': 'enter'}), highlight: true)),
                  const SizedBox(width: 6),
                  Expanded(child: _keyBtn('BACKSPACE', () => _pc.sendAction('press_key', {'key': 'backspace'}))),
                  const SizedBox(width: 6),
                  Expanded(child: _keyBtn('ESC', () => _pc.sendAction('press_key', {'key': 'escape'}))),
                  const SizedBox(width: 6),
                  Expanded(child: _keyBtn('SPACE', () => _pc.sendAction('press_key', {'key': 'space'}))),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(child: _keyBtn('COPY (Ctrl+C)', () => _pc.sendAction('hotkey', {'hotkey': 'copy'}))),
                  const SizedBox(width: 6),
                  Expanded(child: _keyBtn('PASTE (Ctrl+V)', () => _pc.sendAction('hotkey', {'hotkey': 'paste'}))),
                  const SizedBox(width: 6),
                  Expanded(child: _keyBtn('ALT + TAB', () => _pc.sendAction('hotkey', {'hotkey': 'alt_tab'}))),
                ],
              ),
              const SizedBox(height: 12),

              // Arrow Navigation
              Center(
                child: Column(
                  children: [
                    _arrowBtn(Icons.arrow_upward_rounded, () => _pc.sendAction('press_key', {'key': 'up'})),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _arrowBtn(Icons.arrow_back_rounded, () => _pc.sendAction('press_key', {'key': 'left'})),
                        const SizedBox(width: 8),
                        _arrowBtn(Icons.arrow_downward_rounded, () => _pc.sendAction('press_key', {'key': 'down'})),
                        const SizedBox(width: 8),
                        _arrowBtn(Icons.arrow_forward_rounded, () => _pc.sendAction('press_key', {'key': 'right'})),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _keyBtn(String label, VoidCallback onTap, {bool highlight = false}) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: highlight ? const Color(0xFF6366F1) : const Color(0xFF090D16),
        foregroundColor: Colors.white,
        side: BorderSide(color: highlight ? const Color(0xFF6366F1) : const Color(0xFF1E293B)),
        padding: const EdgeInsets.symmetric(vertical: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  Widget _arrowBtn(IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 48,
        height: 38,
        decoration: BoxDecoration(
          color: const Color(0xFF090D16),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF1E293B)),
        ),
        child: Icon(icon, color: const Color(0xFF38BDF8), size: 20),
      ),
    );
  }
}

