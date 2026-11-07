import 'dart:async';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
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
  final AudioRecorder _audioRecorder = AudioRecorder();

  bool _isRecordingVoiceNote = false;
  int _voiceDuration = 0;
  Timer? _voiceTimer;
  bool _isSending = false;

  @override
  void dispose() {
    _voiceTimer?.cancel();
    _audioRecorder.dispose();
    _controller.dispose();
    super.dispose();
  }

  String _formatDuration(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Future<void> _startVoiceNoteRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final tempDir = await getTemporaryDirectory();
        final path = '${tempDir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.aacLc),
          path: path,
        );
        setState(() {
          _isRecordingVoiceNote = true;
          _voiceDuration = 0;
        });
        _voiceTimer?.cancel();
        _voiceTimer = Timer.periodic(const Duration(seconds: 1), (t) {
          if (mounted) setState(() => _voiceDuration++);
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Mic permission error: $e')),
        );
      }
    }
  }

  Future<void> _stopAndSendVoiceNote() async {
    _voiceTimer?.cancel();
    try {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecordingVoiceNote = false;
        _isSending = true;
      });
      if (path != null) {
        final ok = await _pcService.sendVoiceNoteToPC(path, autoPlay: true);
        setState(() => _isSending = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(ok ? '🎙️ Voice note PC par send aur play ho gaya!' : '❌ Failed to send voice note'),
              backgroundColor: ok ? const Color(0xFF10B981) : const Color(0xFFEF4444),
            ),
          );
        }
      } else {
        setState(() => _isSending = false);
      }
    } catch (e) {
      setState(() {
        _isRecordingVoiceNote = false;
        _isSending = false;
      });
    }
  }

  Future<void> _cancelVoiceNote() async {
    _voiceTimer?.cancel();
    await _audioRecorder.stop();
    setState(() => _isRecordingVoiceNote = false);
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
          if (!_isRecordingVoiceNote)
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
                const SizedBox(width: 6),

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
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
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
                            fontSize: 11,
                          ),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(width: 6),

                // AI Command Mic Button
                ValueListenableBuilder<bool>(
                  valueListenable: _voiceService.isListeningNotifier,
                  builder: (context, isListening, _) {
                    return GestureDetector(
                      onTap: _toggleMic,
                      child: Tooltip(
                        message: 'Speech Command Input',
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: isListening ? const Color(0xFFEF4444) : const Color(0xFF6366F1),
                            shape: BoxShape.circle,
                            boxShadow: isListening
                                ? [
                                    BoxShadow(
                                      color: const Color(0xFFEF4444).withValues(alpha: 0.5),
                                      blurRadius: 16,
                                      spreadRadius: 4,
                                    )
                                  ]
                                : [],
                          ),
                          child: Icon(
                            isListening ? Icons.mic : Icons.mic_none,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(width: 6),

                // 🎙️ Dedicated Audio Voice Note Mic Button
                GestureDetector(
                  onTap: _isSending ? null : _startVoiceNoteRecording,
                  child: Tooltip(
                    message: 'Record Real Voice & Send to PC',
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: const BoxDecoration(
                        color: Color(0xFF7C3AED),
                        shape: BoxShape.circle,
                      ),
                      child: _isSending
                          ? const Center(child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)))
                          : const Icon(Icons.record_voice_over_rounded, color: Colors.white, size: 20),
                    ),
                  ),
                ),
                const SizedBox(width: 4),

                // Send button
                IconButton(
                  onPressed: () => _submit(_controller.text),
                  icon: const Icon(Icons.send_rounded, color: Color(0xFF6366F1), size: 20),
                  tooltip: 'Send Command',
                ),
              ],
            )
          else
            // Active Voice Note Recording Strip
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF450A0A),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFEF4444), width: 1.5),
              ),
              child: Row(
                children: [
                  const Icon(Icons.radio_button_checked_rounded, color: Color(0xFFEF4444), size: 20),
                  const SizedBox(width: 8),
                  Text(
                    '● REC: ${_formatDuration(_voiceDuration)}',
                    style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFFCA5A5), fontSize: 13),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Bolye, PC par save & play hoga...',
                      style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _stopAndSendVoiceNote,
                    icon: const Icon(Icons.send_rounded, size: 14),
                    label: const Text('Send 🚀', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      visualDensity: VisualDensity.compact,
                    ),
                  ),
                  const SizedBox(width: 4),
                  IconButton(
                    onPressed: _cancelVoiceNote,
                    icon: const Icon(Icons.close_rounded, color: Colors.grey, size: 18),
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),
            ),
          const SizedBox(height: 10),

          // Quick Action Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildChip('🎙️ Record Voice Note', _startVoiceNoteRecording, borderColor: const Color(0xFFA855F7)),
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

