import 'dart:async';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../../services/pc_service.dart';

class FilesClipboardTab extends StatefulWidget {
  const FilesClipboardTab({super.key});

  @override
  State<FilesClipboardTab> createState() => _FilesClipboardTabState();
}

class _FilesClipboardTabState extends State<FilesClipboardTab> {
  final PCService _pc = PCService();
  final TextEditingController _clipboardCtrl = TextEditingController();
  final AudioRecorder _audioRecorder = AudioRecorder();

  bool _isUploading = false;
  String _uploadStatus = '';
  List<Map<String, dynamic>> _receivedFiles = [];

  bool _isRecordingVoice = false;
  int _recordDuration = 0;
  Timer? _recordTimer;
  bool _isSendingVoice = false;

  @override
  void initState() {
    super.initState();
    _loadReceivedFiles();
  }

  @override
  void dispose() {
    _recordTimer?.cancel();
    _audioRecorder.dispose();
    _clipboardCtrl.dispose();
    super.dispose();
  }

  String _formatDuration(int sec) {
    final m = (sec ~/ 60).toString().padLeft(2, '0');
    final s = (sec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Future<void> _startVoiceRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final tempDir = await getTemporaryDirectory();
        final path = '${tempDir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.aacLc),
          path: path,
        );
        setState(() {
          _isRecordingVoice = true;
          _recordDuration = 0;
          _uploadStatus = '🎙️ Voice record ho rahi hai... Bolye!';
        });
        _recordTimer?.cancel();
        _recordTimer = Timer.periodic(const Duration(seconds: 1), (t) {
          if (mounted) setState(() => _recordDuration++);
        });
      }
    } catch (e) {
      setState(() => _uploadStatus = 'Mic error: $e');
    }
  }

  Future<void> _stopAndSendVoice() async {
    _recordTimer?.cancel();
    try {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecordingVoice = false;
        _isSendingVoice = true;
        _uploadStatus = 'PC par voice note bheja ja raha hai...';
      });
      if (path != null) {
        final ok = await _pc.sendVoiceNoteToPC(path, autoPlay: true);
        setState(() {
          _isSendingVoice = false;
          _uploadStatus = ok ? '🎙️ Voice note PC par send aur play ho gaya!' : '❌ Failed to send voice note';
        });
        if (ok) {
          _loadReceivedFiles();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('🎙️ Voice note PC par send aur play ho gaya!'),
                backgroundColor: Color(0xFF10B981),
              ),
            );
          }
        }
      } else {
        setState(() => _isSendingVoice = false);
      }
    } catch (e) {
      setState(() {
        _isRecordingVoice = false;
        _isSendingVoice = false;
        _uploadStatus = 'Voice error: $e';
      });
    }
  }

  Future<void> _cancelVoiceRecording() async {
    _recordTimer?.cancel();
    await _audioRecorder.stop();
    setState(() {
      _isRecordingVoice = false;
      _uploadStatus = 'Recording cancel kar di gayi';
    });
  }

  Future<void> _loadReceivedFiles() async {
    final list = await _pc.fetchFileList();
    if (mounted) {
      setState(() => _receivedFiles = list);
    }
  }

  Future<void> _pickAndUploadFile() async {
    try {
      final files = await FilePicker.pickFiles();
      if (files.isNotEmpty && files.first.path != null) {
        final path = files.first.path!;
        final name = files.first.name;

        setState(() {
          _isUploading = true;
          _uploadStatus = 'Uploading $name to PC...';
        });

        final ok = await _pc.uploadFileToPC(path, name);
        setState(() {
          _isUploading = false;
          _uploadStatus = ok ? '✅ "$name" saved to PC Downloads!' : '❌ Upload failed';
        });

        if (ok) {
          _loadReceivedFiles();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('File "$name" sent to PC!'), backgroundColor: const Color(0xFF10B981)),
            );
          }
        }
      }
    } catch (e) {
      setState(() {
        _isUploading = false;
        _uploadStatus = 'Error: $e';
      });
    }
  }

  Future<void> _fetchPCClipboard() async {
    final text = await _pc.fetchPCClipboard();
    _clipboardCtrl.text = text;
    if (text.isNotEmpty) {
      await Clipboard.setData(ClipboardData(text: text));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📋 PC Clipboard copied to Phone!'), backgroundColor: Color(0xFF10B981)),
        );
      }
    }
  }

  Future<void> _sendPhoneClipboardToPC() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    final text = data?.text ?? _clipboardCtrl.text;
    if (text.isNotEmpty) {
      final ok = await _pc.sendPCClipboard(text);
      if (ok && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('🖥️ Text sent to PC Clipboard (Ctrl+V ready)!'), backgroundColor: Color(0xFF6366F1)),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // 🎙️ Voice Note Recorder & Sender Card
        if (!_isRecordingVoice)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E1B4B), Color(0xFF131C2E)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF4338CA)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.mic_none_rounded, color: Color(0xFFA855F7), size: 22),
                    SizedBox(width: 8),
                    Text(
                      '🎙️ Live Voice Note Sender',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'Mobile me bolein. Band karte hi foran PC par voice note save aur play ho jayega.',
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isSendingVoice ? null : _startVoiceRecording,
                    icon: _isSendingVoice
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.mic_rounded, size: 20),
                    label: Text(
                      _isSendingVoice ? 'Sending to PC...' : '🎤 Tap to Record Voice Note',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF7C3AED),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),
          )
        else
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF450A0A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFDC2626), width: 2),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.radio_button_checked_rounded, color: Color(0xFFEF4444), size: 22),
                        const SizedBox(width: 8),
                        Text(
                          '● RECORDING: ${_formatDuration(_recordDuration)}',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFFFCA5A5)),
                        ),
                      ],
                    ),
                    const Text('PC par send hone k liye ready', style: TextStyle(fontSize: 10, color: Colors.grey)),
                  ],
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: ElevatedButton.icon(
                        onPressed: _stopAndSendVoice,
                        icon: const Icon(Icons.send_rounded, size: 18),
                        label: const Text('Stop & Send to PC 🚀', style: TextStyle(fontWeight: FontWeight.bold)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10B981),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _cancelVoiceRecording,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFFCA5A5),
                          side: const BorderSide(color: Color(0xFFEF4444)),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: const Text('Cancel'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        const SizedBox(height: 12),

        // Universal Shared Clipboard Card
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
                  Icon(Icons.assignment_rounded, color: Color(0xFF6366F1), size: 20),
                  SizedBox(width: 8),
                  Text(
                    '📋 Universal Shared Clipboard',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Mobile se PC par aur PC se mobile par clipboard text sync karein.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _clipboardCtrl,
                maxLines: 2,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  hintText: 'Clipboard text preview...',
                  hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  filled: true,
                  fillColor: const Color(0xFF090D16),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _sendPhoneClipboardToPC,
                      icon: const Icon(Icons.arrow_upward_rounded, size: 16),
                      label: const Text('Send to PC'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF6366F1),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 11),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _fetchPCClipboard,
                      icon: const Icon(Icons.arrow_downward_rounded, size: 16),
                      label: const Text('Fetch from PC'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E293B),
                        foregroundColor: const Color(0xFF38BDF8),
                        padding: const EdgeInsets.symmetric(vertical: 11),
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

        // Wireless File Drop Card (AirDrop for PC)
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.send_to_mobile_rounded, color: Color(0xFF10B981), size: 20),
                  SizedBox(width: 8),
                  Text(
                    '📁 Wireless File Drop (To PC Downloads)',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Mobile se photo, video ya file bhejein — PC ke Downloads folder me direct save hogi.',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isUploading ? null : _pickAndUploadFile,
                  icon: _isUploading
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.upload_file_rounded, size: 20),
                  label: Text(_isUploading ? 'Sending File to PC...' : '📤 Pick & Send File to PC'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF059669),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              if (_uploadStatus.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(_uploadStatus, style: const TextStyle(fontSize: 12, color: Color(0xFF38BDF8))),
              ],
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('📂 Files on PC Received Folder', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, size: 18, color: Colors.grey),
                    onPressed: _loadReceivedFiles,
                  ),
                ],
              ),
              if (_receivedFiles.isEmpty)
                Text('No files sent yet.', style: TextStyle(color: Colors.grey.shade600, fontSize: 11))
              else
                Column(
                  children: _receivedFiles.take(5).map((f) {
                    final name = f['name'] ?? '';
                    final size = f['size_mb'] ?? 0;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 4),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: const Color(0xFF090D16),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.insert_drive_file_rounded, color: Colors.grey, size: 16),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(name.toString(), style: const TextStyle(color: Colors.white, fontSize: 12), overflow: TextOverflow.ellipsis),
                          ),
                          Text('$size MB', style: TextStyle(color: Colors.grey.shade500, fontSize: 10)),
                        ],
                      ),
                    );
                  }).toList(),
                ),
            ],
          ),
        ),
      ],
    );
  }
}
