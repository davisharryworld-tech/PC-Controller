import 'package:flutter/material.dart';
import '../../services/pc_service.dart';

class RunningAppsTab extends StatefulWidget {
  const RunningAppsTab({super.key});

  @override
  State<RunningAppsTab> createState() => _RunningAppsTabState();
}

class _RunningAppsTabState extends State<RunningAppsTab> {
  final PCService _pc = PCService();
  final TextEditingController _killCtrl = TextEditingController();

  List<Map<String, dynamic>> _apps = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadApps();
  }

  @override
  void dispose() {
    _killCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadApps() async {
    setState(() => _isLoading = true);
    final list = await _pc.fetchRunningApps();
    if (mounted) {
      setState(() {
        _apps = list;
        _isLoading = false;
      });
    }
  }

  void _closeApp(String shortId) {
    _pc.sendAction('close_app', {'name': shortId});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Closing $shortId...'), duration: const Duration(seconds: 1)),
    );
    Future.delayed(const Duration(milliseconds: 800), _loadApps);
  }

  void _killCustom() {
    final name = _killCtrl.text.trim();
    if (name.isNotEmpty) {
      _closeApp(name);
      _killCtrl.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        // Custom App Kill
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
                '❌ Close Specific Program',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _killCtrl,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: InputDecoration(
                        hintText: 'e.g. chrome, notepad, vlc, discord...',
                        hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                        filled: true,
                        fillColor: const Color(0xFF090D16),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onSubmitted: (_) => _killCustom(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _killCustom,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFEF4444),
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Kill App', style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Running Apps List Card
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
                    'Active User Applications',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: Color(0xFF38BDF8)),
                    tooltip: 'Refresh',
                    onPressed: _loadApps,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (_isLoading)
                const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()))
              else if (_apps.isEmpty)
                Text(
                  'No user applications currently detected on PC.',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                )
              else
                ..._apps.map(
                  (app) => Container(
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
                        Text(
                          '${app['icon'] ?? '📱'} ${app['display_name'] ?? 'App'}',
                          style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                        ElevatedButton(
                          onPressed: () => _closeApp(app['short_id'] ?? ''),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFEF4444),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            minimumSize: Size.zero,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                          ),
                          child: const Text('Close', style: TextStyle(color: Colors.white, fontSize: 11)),
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
