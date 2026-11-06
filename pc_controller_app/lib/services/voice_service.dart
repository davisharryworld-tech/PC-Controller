import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class VoiceService {
  static final VoiceService _instance = VoiceService._internal();
  factory VoiceService() => _instance;
  VoiceService._internal();

  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isAvailable = false;
  final ValueNotifier<bool> isListeningNotifier = ValueNotifier<bool>(false);
  final ValueNotifier<String> transcribedTextNotifier = ValueNotifier<String>('');
  final ValueNotifier<String> selectedLanguageNotifier = ValueNotifier<String>('ur_PK');

  bool get isAvailable => _isAvailable;

  Future<bool> initialize() async {
    try {
      _isAvailable = await _speech.initialize(
        onError: (val) {
          isListeningNotifier.value = false;
        },
        onStatus: (status) {
          if (status == 'done' || status == 'notListening') {
            isListeningNotifier.value = false;
          }
        },
      );
      return _isAvailable;
    } catch (_) {
      return false;
    }
  }

  void toggleLanguage() {
    if (selectedLanguageNotifier.value == 'ur_PK') {
      selectedLanguageNotifier.value = 'en_US';
    } else {
      selectedLanguageNotifier.value = 'ur_PK';
    }
  }

  Future<void> startListening({required Function(String text) onResultReady}) async {
    if (!_isAvailable) {
      final ok = await initialize();
      if (!ok) return;
    }

    if (_speech.isListening) {
      await stopListening();
      return;
    }

    transcribedTextNotifier.value = '';
    isListeningNotifier.value = true;

    try {
      await _speech.listen(
        onResult: (result) {
          transcribedTextNotifier.value = result.recognizedWords;
          if (result.finalResult && result.recognizedWords.isNotEmpty) {
            onResultReady(result.recognizedWords);
            stopListening();
          }
        },
        listenOptions: stt.SpeechListenOptions(
          listenMode: stt.ListenMode.confirmation,
          localeId: selectedLanguageNotifier.value,
        ),
      );
    } catch (_) {
      isListeningNotifier.value = false;
    }
  }

  Future<void> stopListening() async {
    if (_speech.isListening) {
      await _speech.stop();
    }
    isListeningNotifier.value = false;
  }
}
