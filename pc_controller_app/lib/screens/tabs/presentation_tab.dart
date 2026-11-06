import 'package:flutter/material.dart';
import '../../services/pc_service.dart';

class PresentationTab extends StatefulWidget {
  const PresentationTab({super.key});

  @override
  State<PresentationTab> createState() => _PresentationTabState();
}

class _PresentationTabState extends State<PresentationTab> {
  final PCService _pc = PCService();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          // Header Card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF131C2E),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1E293B)),
            ),
            child: const Row(
              children: [
                Icon(Icons.slideshow_rounded, color: Color(0xFFF59E0B), size: 22),
                SizedBox(width: 8),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '📊 Presentation & Slides Clicker',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'PowerPoint, Google Slides aur PDF presentations control karein.',
                      style: TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Big Next and Previous Buttons
          Expanded(
            child: Row(
              children: [
                // PREV Slide Button
                Expanded(
                  child: InkWell(
                    onTap: () => _pc.sendAction('presentation_prev'),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF334155), width: 2),
                      ),
                      child: const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.arrow_back_ios_new_rounded, size: 48, color: Color(0xFF38BDF8)),
                          SizedBox(height: 12),
                          Text('PREVIOUS', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                          SizedBox(height: 4),
                          Text('(PageUp)', style: TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 14),

                // NEXT Slide Button
                Expanded(
                  child: InkWell(
                    onTap: () => _pc.sendAction('presentation_next'),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF6366F1), Color(0xFF4F46E5)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: const [
                          BoxShadow(color: Color(0x666366F1), blurRadius: 16, offset: Offset(0, 4)),
                        ],
                      ),
                      child: const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.arrow_forward_ios_rounded, size: 48, color: Colors.white),
                          SizedBox(height: 12),
                          Text('NEXT SLIDE', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                          SizedBox(height: 4),
                          Text('(PageDown)', style: TextStyle(fontSize: 12, color: Colors.white70)),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Slide Controls (F5, Esc, Black Screen)
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendAction('presentation_start'),
                  icon: const Icon(Icons.play_circle_fill_rounded, size: 18),
                  label: const Text('Start (F5)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF059669),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendAction('presentation_black'),
                  icon: const Icon(Icons.contrast_rounded, size: 18),
                  label: const Text('Black (B)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E293B),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _pc.sendAction('presentation_exit'),
                  icon: const Icon(Icons.close_rounded, size: 18),
                  label: const Text('Exit (Esc)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEF4444).withValues(alpha: 0.2),
                    foregroundColor: const Color(0xFFFCA5A5),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

