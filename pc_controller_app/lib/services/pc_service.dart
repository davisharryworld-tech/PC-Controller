import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

enum ConnectionStatus { disconnected, connecting, connected }

class PCService {
  static final PCService _instance = PCService._internal();
  factory PCService() => _instance;
  PCService._internal();

  // Network Configuration
  String _host = '10.168.124.10';
  int _port = 8000;
  String _tailscaleIp = '100.70.0.109';
  bool _useTailscale = true;

  // Exclusive Hardware Device Token (Locks access to Honor X6c)
  static const String authorizedDeviceToken = 'HX6C-982341-EXCLUSIVE-HONOR-TOKEN';

  Map<String, String> get authHeaders => {
    'X-Device-Token': authorizedDeviceToken,
  };

  String get activeHost => _useTailscale ? _tailscaleIp : _host;
  int get port => _port;
  bool get useTailscale => _useTailscale;
  String get httpBaseUrl => 'http://$activeHost:$_port';
  String get wsUrl => 'ws://$activeHost:$_port/ws/controller?token=$authorizedDeviceToken';

  // Connection State
  final ValueNotifier<ConnectionStatus> statusNotifier =
      ValueNotifier<ConnectionStatus>(ConnectionStatus.disconnected);
  final ValueNotifier<String> lastMessageNotifier = ValueNotifier<String>('');
  final ValueNotifier<List<String>> logsNotifier = ValueNotifier<List<String>>([]);

  WebSocketChannel? _channel;
  StreamSubscription? _channelSub;
  Timer? _reconnectTimer;
  Timer? _pingTimer;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _host = prefs.getString('pc_host') ?? '10.168.124.10';
    _port = prefs.getInt('pc_port') ?? 8000;
    _tailscaleIp = prefs.getString('pc_tailscale') ?? '100.70.0.109';
    _useTailscale = prefs.getBool('use_tailscale') ?? true;

    connect();
  }

  Future<void> updateConfig({
    required String host,
    required int port,
    required String tailscaleIp,
    required bool useTailscale,
  }) async {
    _host = host;
    _port = port;
    _tailscaleIp = tailscaleIp;
    _useTailscale = useTailscale;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('pc_host', _host);
    await prefs.setInt('pc_port', _port);
    await prefs.setString('pc_tailscale', _tailscaleIp);
    await prefs.setBool('use_tailscale', _useTailscale);

    disconnect();
    connect();
  }

  void connect() {
    if (statusNotifier.value == ConnectionStatus.connected) return;

    statusNotifier.value = ConnectionStatus.connecting;
    _addLog('Connecting to $wsUrl...');

    try {
      final uri = Uri.parse(wsUrl);
      _channel = WebSocketChannel.connect(uri);

      _channelSub = _channel!.stream.listen(
        (data) {
          _onData(data);
        },
        onError: (err) {
          _addLog('WebSocket error: $err');
          _onDisconnected();
        },
        onDone: () {
          _addLog('WebSocket closed.');
          _onDisconnected();
        },
      );

      // Send initial handshake
      sendHandshake();

      statusNotifier.value = ConnectionStatus.connected;
      _addLog('Connected to Windows PC Agent! 🟢');

      // Start ping heartbeat
      _pingTimer?.cancel();
      _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
        sendPing();
      });
    } catch (e) {
      _addLog('Connection failed: $e');
      _onDisconnected();
    }
  }

  void _onData(dynamic data) {
    try {
      final jsonMap = jsonDecode(data.toString()) as Map<String, dynamic>;
      final type = jsonMap['type'] ?? '';
      final payload = jsonMap['payload'] ?? {};

      if (type == 'action_result') {
        final msg = payload['message'] ?? 'Action completed';
        lastMessageNotifier.value = msg.toString();
        _addLog('Result: $msg');
      } else if (type == 'welcome') {
        final server = payload['server'] ?? 'PC Agent';
        _addLog('Welcome: $server ready');
      }
    } catch (e) {
      _addLog('Receive error: $e');
    }
  }

  int _retryCount = 0;

  void _onDisconnected() {
    statusNotifier.value = ConnectionStatus.disconnected;
    _pingTimer?.cancel();
    _channelSub?.cancel();
    _channel = null;

    _retryCount++;
    // If 2 attempts fail on one IP, try the other IP automatically
    if (_retryCount >= 2) {
      _retryCount = 0;
      _useTailscale = !_useTailscale;
      _addLog('Switching network mode to: ${_useTailscale ? "Tailscale (100.70.0.109)" : "Local Wi-Fi (10.168.124.10)"}');
    }

    // Auto reconnect every 3 seconds
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      if (statusNotifier.value == ConnectionStatus.disconnected) {
        connect();
      }
    });
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _channelSub?.cancel();
    _channel?.sink.close();
    _channel = null;
    statusNotifier.value = ConnectionStatus.disconnected;
  }

  void _addLog(String text) {
    final list = List<String>.from(logsNotifier.value);
    list.insert(0, text);
    if (list.length > 50) list.removeLast();
    logsNotifier.value = list;
  }

  void sendHandshake() {
    _sendJson({
      'type': 'handshake',
      'device_id': 'honor_x6c_exclusive',
      'payload': {
        'device_name': 'Honor X6c',
        'device_token': authorizedDeviceToken,
      }
    });
  }

  void sendPing() {
    _sendJson({
      'type': 'ping',
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });
  }

  void sendCommand(String query) {
    if (query.trim().isEmpty) return;
    _addLog('Voice Command: "$query"');
    _sendJson({
      'type': 'command',
      'payload': {'query': query.trim()}
    });
  }

  void sendAction(String action, [Map<String, dynamic>? extra]) {
    final payload = <String, dynamic>{'action': action};
    if (extra != null) payload.addAll(extra);
    _sendJson({
      'type': 'action',
      'payload': payload,
    });
  }

  void sendMouseMove(int dx, int dy) {
    _sendJson({
      'type': 'action',
      'payload': {'action': 'mouse_move', 'dx': dx, 'dy': dy}
    });
  }

  void _sendJson(Map<String, dynamic> data) {
    if (_channel != null && statusNotifier.value == ConnectionStatus.connected) {
      try {
        _channel!.sink.add(jsonEncode(data));
      } catch (e) {
        _addLog('Send error: $e');
      }
    } else {
      _addLog('PC is not connected!');
    }
  }

  // REST API Helpers
  Future<Map<String, dynamic>> fetchSystemInfo() async {
    try {
      final res = await http.get(Uri.parse('$httpBaseUrl/api/system'));
      if (res.statusCode == 200) {
        return jsonDecode(res.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {};
  }

  Future<Map<String, String>> fetchContacts() async {
    try {
      final res = await http.get(Uri.parse('$httpBaseUrl/api/contacts'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final contacts = data['contacts'] as Map<String, dynamic>? ?? {};
        return contacts.map((k, v) => MapEntry(k, v.toString()));
      }
    } catch (_) {}
    return {};
  }

  Future<bool> saveContact(String name, String phone) async {
    try {
      final res = await http.post(
        Uri.parse('$httpBaseUrl/api/contacts'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': name, 'phone': phone}),
      );
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteContact(String name) async {
    try {
      final res = await http.delete(Uri.parse('$httpBaseUrl/api/contacts/$name'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> fetchRunningApps() async {
    try {
      final res = await http.get(Uri.parse('$httpBaseUrl/api/running_apps'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final apps = data['apps'] as List<dynamic>? ?? [];
        return apps.cast<Map<String, dynamic>>();
      }
    } catch (_) {}
    return [];
  }

  // --- NEW CAPABILITIES ---

  String get screenStreamUrl => '$httpBaseUrl/api/screen/stream?token=$authorizedDeviceToken';
  String get screenshotUrl => '$httpBaseUrl/api/screen/screenshot?token=$authorizedDeviceToken';

  Future<String> fetchPCClipboard() async {
    try {
      final res = await http.get(
        Uri.parse('$httpBaseUrl/api/clipboard'),
        headers: authHeaders,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        return data['clipboard']?.toString() ?? '';
      }
    } catch (_) {}
    return '';
  }

  Future<bool> sendPCClipboard(String text) async {
    try {
      final headers = <String, String>{'Content-Type': 'application/json'};
      headers.addAll(authHeaders);
      final res = await http.post(
        Uri.parse('$httpBaseUrl/api/clipboard'),
        headers: headers,
        body: jsonEncode({'text': text}),
      );
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> fetchWolInfo() async {
    try {
      final res = await http.get(
        Uri.parse('$httpBaseUrl/api/system/wol-info'),
        headers: authHeaders,
      );
      if (res.statusCode == 200) {
        return jsonDecode(res.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {};
  }

  Future<bool> sendWakeOnLan(String macAddress) async {
    try {
      final cleanMac = macAddress.replaceAll(RegExp(r'[^0-9A-Fa-f]'), '');
      if (cleanMac.length != 12) return false;
      final macBytes = <int>[];
      for (int i = 0; i < 12; i += 2) {
        macBytes.add(int.parse(cleanMac.substring(i, i + 2), radix: 16));
      }
      final packet = <int>[...List.filled(6, 0xFF)];
      for (int i = 0; i < 16; i++) {
        packet.addAll(macBytes);
      }
      final socket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
      socket.broadcastEnabled = true;
      socket.send(packet, InternetAddress('255.255.255.255'), 9);
      socket.close();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> sendVoiceNoteToPC(String filePath, {bool autoPlay = true}) async {
    try {
      final uri = Uri.parse('$httpBaseUrl/api/voice/send?auto_play=$autoPlay');
      final request = http.MultipartRequest('POST', uri);
      request.headers.addAll(authHeaders);
      final fileName = filePath.split(Platform.pathSeparator).last;
      request.files.add(await http.MultipartFile.fromPath('file', filePath, filename: fileName));
      final response = await request.send();
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<bool> uploadFileToPC(String filePath, String fileName) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$httpBaseUrl/api/files/upload'));
      request.headers.addAll(authHeaders);
      request.files.add(await http.MultipartFile.fromPath('file', filePath, filename: fileName));
      final response = await request.send();
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> fetchFileList() async {
    try {
      final res = await http.get(
        Uri.parse('$httpBaseUrl/api/files/list'),
        headers: authHeaders,
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final files = data['files'] as List<dynamic>? ?? [];
        return files.cast<Map<String, dynamic>>();
      }
    } catch (_) {}
    return [];
  }
}

