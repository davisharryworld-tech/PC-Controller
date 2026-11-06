import 'package:flutter/material.dart';
import '../services/pc_service.dart';
import '../services/voice_service.dart';

class VoiceControlBar extends StatefulWidget {
  const VoiceControlBar({super.key});

  @override
  State<VoiceControlBar> createState() => _VoiceControlBarState();
}

class _VoiceControlBarState extends State<VoiceControlBar> {
  final TextEditingController _controller = TextEditingController();
  final PCService _pcService = PCService();
  final VoiceService _voiceService = VoiceService();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit(String text) {
    if (text.trim().isEmpty) return;
    _pcService.sendCommand(text);
    _controller.clear();
  }

  void _toggleMic() {
    _voiceService.startListening(
      onResultReady: (text) {
        _controller.text = text;
        _submit(text);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF131C2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: ValueListenableBuilder<String>(
                  valueListenable: _voiceService.transcribedTextNotifier,
                  builder: (context, spoken, _) {
                    if (spoken.isNotEmpty && _controller.text != spoken) {
                      _controller.text = spoken;
                    }
                    return TextField(
                      controller: _controller,
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: "Bolye ya likhein: 'open chat gpt', 'ali ki chat'...",
                        hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 13),
                        filled: true,
                        fillColor: const Color(0xFF090D16),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF1E293B)),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF1E293B)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
                        ),
                      ),
                      onSubmitted: _submit,
                    );
                  },
                ),
              ),
              const SizedBox(width: 8),

              // Language toggle button (UR / EN)
              ValueListenableBuilder<String>(
                valueListenable: _voiceService.selectedLanguageNotifier,
                builder: (context, lang, _) {
                  final isUrdu = lang == 'ur_PK';
                  return InkWell(
                    onTap: () {
                      _voiceService.toggleLanguage();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(isUrdu ? '🌐 Voice switched to English mode' : '🌐 Voice switched to Urdu (اردو) mode'),
                          duration: const Duration(seconds: 1),
                        ),
                      );
                    },
                    borderRadius: BorderRadius.circular(10),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: isUrdu ? const Color(0xFF4ADE80) : const Color(0xFF38BDF8)),
                      ),
                      child: Text(
                        isUrdu ? '🌐 UR' : '🌐 EN',
                        style: TextStyle(
                          color: isUrdu ? const Color(0xFF4ADE80) : const Color(0xFF38BDF8),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(width: 8),

              // Mic Button
              ValueListenableBuilder<bool>(
                valueListenable: _voiceService.isListeningNotifier,
                builder: (context, isListening, _) {
                  return GestureDetector(
                    onTap: _toggleMic,
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: isListening ? const Color(0xFFEF4444) : const Color(0xFF6366F1),
                        shape: BoxShape.circle,
                        boxShadow: isListening
                            ? [
                                BoxShadow(
                                  color: const Color(0xFFEF4444).withOpacity(0.5),
                                  blurRadius: 16,
                                  spreadRadius: 4,
                                )
                              ]
                            : [],
                      ),
                      child: Icon(
                        isListening ? Icons.mic : Icons.mic_none,
                        color: Colors.white,
                        size: 22,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(width: 8),

              // Send button
              IconButton(
                onPressed: () => _submit(_controller.text),
                icon: const Icon(Icons.send_rounded, color: Color(0xFF6366F1)),
                tooltip: 'Send Command',
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Quick Action Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildChip('🤖 ChatGPT', () => _submit('open chat gpt'), borderColor: const Color(0xFF10B981)),
                _buildChip('▶️ YouTube', () => _submit('open youtube')),
                _buildChip('💬 My Chat', () => _submit('open my number chat')),
                _buildChip('🎵 Play Songs', () => _submit('open youtube and play songs')),
                _buildChip('🔊 Vol +', () => _submit('volume up')),
                _buildChip('🔉 Vol -', () => _submit('volume down')),
                _buildChip('🔇 Mute', () => _submit('volume mute')),
                _buildChip('🌐 Chrome', () => _submit('open chrome')),
                _buildChip('❌ Close', () => _submit('close')),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(String label, VoidCallback onTap, {Color? borderColor}) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ActionChip(
        label: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: borderColor ?? Colors.grey.shade300,
          ),
        ),
        backgroundColor: const Color(0xFF090D16),
        side: BorderSide(color: borderColor ?? const Color(0xFF1E293B)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        onPressed: onTap,
      ),
    );
  }
}

