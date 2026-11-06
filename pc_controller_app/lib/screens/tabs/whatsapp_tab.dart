import 'package:flutter/material.dart';
import '../../services/pc_service.dart';
import '../../services/voice_service.dart';

class WhatsAppTab extends StatefulWidget {
  const WhatsAppTab({super.key});

  @override
  State<WhatsAppTab> createState() => _WhatsAppTabState();
}

class _WhatsAppTabState extends State<WhatsAppTab> {
  final TextEditingController _recipientController = TextEditingController();
  final TextEditingController _messageController = TextEditingController();
  final PCService _pc = PCService();
  final VoiceService _voice = VoiceService();

  Map<String, String> _contacts = {};
  bool _isLoadingContacts = false;

  @override
  void initState() {
    super.initState();
    _loadContacts();
  }

  @override
  void dispose() {
    _recipientController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _loadContacts() async {
    setState(() => _isLoadingContacts = true);
    final list = await _pc.fetchContacts();
    if (mounted) {
      setState(() {
        _contacts = list;
        _isLoadingContacts = false;
      });
    }
  }

  void _dictateMessage() {
    _voice.startListening(
      onResultReady: (text) {
        setState(() {
          final current = _messageController.text;
          _messageController.text = current.isEmpty ? text : '$current $text';
        });
      },
    );
  }

  void _sendWhatsApp() {
    final rec = _recipientController.text.trim();
    final msg = _messageController.text.trim();
    if (rec.isEmpty || msg.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('⚠️ Recipient aur message dono required hain')),
      );
      return;
    }

    _pc.sendAction('whatsapp_send', {'recipient': rec, 'message': msg});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('💬 Message sent to $rec')),
    );
  }

  void _openChatOnly() {
    final rec = _recipientController.text.trim();
    if (rec.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('⚠️ Recipient name ya number likhein')),
      );
      return;
    }
    _pc.sendAction('whatsapp_open_chat', {'recipient': rec});
  }

  void _showAddContactDialog() {
    final nameCtrl = TextEditingController();
    final phoneCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF131C2E),
        title: const Text('Save New Contact', style: TextStyle(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: 'Contact Name (e.g. ali, abu, my number)',
                labelStyle: TextStyle(color: Colors.grey),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: phoneCtrl,
              keyboardType: TextInputType.phone,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: 'Phone Number (e.g. 03001234567)',
                labelStyle: TextStyle(color: Colors.grey),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF25D366)),
            onPressed: () async {
              final n = nameCtrl.text.trim();
              final p = phoneCtrl.text.trim();
              if (n.isNotEmpty && p.isNotEmpty) {
                await _pc.saveContact(n, p);
                if (ctx.mounted) Navigator.pop(ctx);
                _loadContacts();
              }
            },
            child: const Text('Save Contact', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Composer Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131C2E),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF25D366).withOpacity(0.35)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.chat_bubble_rounded, color: Color(0xFF25D366), size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Direct WhatsApp Message Sender',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF4ADE80)),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Number ya saved contact name likhein. PC par WhatsApp chat khulegi aur message dispatch hoga.',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
              ),
              const SizedBox(height: 12),

              // Recipient field
              TextField(
                controller: _recipientController,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  labelText: 'Recipient (Phone number ya Saved Name)',
                  labelStyle: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                  hintText: 'e.g. 03001234567, ali, abu, my number...',
                  hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  filled: true,
                  fillColor: const Color(0xFF090D16),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 10),

              // Message field with voice dictate
              TextField(
                controller: _messageController,
                maxLines: 2,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: InputDecoration(
                  labelText: 'Message Body',
                  labelStyle: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                  hintText: 'Type your message...',
                  hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  filled: true,
                  fillColor: const Color(0xFF090D16),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.mic, color: Color(0xFF4ADE80)),
                    tooltip: 'Bol kar likhein',
                    onPressed: _dictateMessage,
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _sendWhatsApp,
                      icon: const Icon(Icons.send_rounded, size: 16),
                      label: const Text('Send Message', style: TextStyle(fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF25D366),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton.icon(
                    onPressed: _openChatOnly,
                    icon: const Icon(Icons.folder_open_rounded, size: 16),
                    label: const Text('Open Chat'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF38BDF8),
                      side: const BorderSide(color: Color(0xFF1E293B)),
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // "Send it" active dispatcher
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendCommand('send it'),
                  icon: const Icon(Icons.done_all_rounded, size: 16),
                  label: const Text('🚀 Send It Now (Dispatch Typed Text)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E293B),
                    foregroundColor: const Color(0xFF4ADE80),
                    padding: const EdgeInsets.symmetric(vertical: 11),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Contacts Manager Card
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
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    '📇 Saved Contacts',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  IconButton(
                    onPressed: _showAddContactDialog,
                    icon: const Icon(Icons.add_circle_outline_rounded, color: Color(0xFF38BDF8)),
                    tooltip: 'Add Contact',
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (_isLoadingContacts)
                const Center(child: Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator()))
              else if (_contacts.isEmpty)
                Text(
                  'Koi contact saved nahi hai. "+" button daba kar save karein.',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                )
              else
                ..._contacts.entries.map(
                  (entry) => Container(
                    margin: const EdgeInsets.only(bottom: 6),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFF090D16),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF1E293B)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        InkWell(
                          onTap: () {
                            setState(() {
                              _recipientController.text = entry.key;
                            });
                          },
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '👤 ${entry.key.toUpperCase()}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF38BDF8),
                                  fontSize: 13,
                                ),
                              ),
                              Text(
                                entry.value,
                                style: TextStyle(color: Colors.grey.shade500, fontSize: 11),
                              ),
                            ],
                          ),
                        ),
                        Row(
                          children: [
                            TextButton(
                              onPressed: () {
                                setState(() {
                                  _recipientController.text = entry.key;
                                });
                              },
                              child: const Text('Select', style: TextStyle(fontSize: 12)),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, size: 18, color: Color(0xFFEF4444)),
                              onPressed: () async {
                                await _pc.deleteContact(entry.key);
                                _loadContacts();
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}
