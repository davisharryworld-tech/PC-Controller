package com.personalai.agent;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.content.Context;
import android.content.Intent;
import android.graphics.Path;
import android.net.Uri;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.net.HttpURLConnection;
import java.util.Collections;
import java.util.List;

public class AgentAccessibilityService extends AccessibilityService {

    public static volatile boolean isServiceRunning = false;
    public static AgentAccessibilityService instance = null;
    public static Context appContext = null;

    private static ServerSocket serverSocket;
    private static Thread serverThread;
    private static boolean isListening = false;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // No-op for passive listening
    }

    @Override
    public void onInterrupt() {
        isServiceRunning = false;
        instance = null;
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        isServiceRunning = true;
        instance = this;
        appContext = getApplicationContext();
        startServer(this);
        registerWithMaster(this);
    }

    @Override
    public void onDestroy() {
        isServiceRunning = false;
        instance = null;
        super.onDestroy();
    }

    public static synchronized void startServer(Context context) {
        if (context != null) appContext = context.getApplicationContext();
        if (isListening && serverSocket != null && !serverSocket.isClosed()) return;
        isListening = true;
        serverThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    serverSocket = new ServerSocket(9090);
                    while (isListening && !serverSocket.isClosed()) {
                        final Socket client = serverSocket.accept();
                        new Thread(new Runnable() {
                            @Override
                            public void run() {
                                handleClient(client);
                            }
                        }).start();
                    }
                } catch (Exception ignored) {}
            }
        });
        serverThread.setDaemon(true);
        serverThread.start();
    }

    public static synchronized void stopServer() {
        isListening = false;
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
        } catch (Exception ignored) {}
    }

    private static void handleClient(Socket socket) {
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String line = reader.readLine();
            if (line == null) {
                socket.close();
                return;
            }

            int contentLength = 0;
            while ((line = reader.readLine()) != null && !line.isEmpty()) {
                if (line.toLowerCase().startsWith("content-length:")) {
                    contentLength = Integer.parseInt(line.substring(15).trim());
                }
            }

            StringBuilder body = new StringBuilder();
            if (contentLength > 0) {
                char[] buf = new char[contentLength];
                int read = reader.read(buf, 0, contentLength);
                if (read > 0) {
                    body.append(buf, 0, read);
                }
            }

            String response = executeCommand(body.toString());
            byte[] responseBytes = response.getBytes("UTF-8");

            OutputStream out = socket.getOutputStream();
            out.write("HTTP/1.1 200 OK\r\n".getBytes());
            out.write("Content-Type: application/json\r\n".getBytes());
            out.write("Access-Control-Allow-Origin: *\r\n".getBytes());
            out.write(("Content-Length: " + responseBytes.length + "\r\n\r\n").getBytes());
            out.write(responseBytes);
            out.flush();
            socket.close();
        } catch (Exception ignored) {
            try { socket.close(); } catch (Exception e) {}
        }
    }

    private static String executeCommand(String json) {
        try {
            if (json.isEmpty() || json.contains("\"action\":\"info\"") || json.contains("\"info\"")) {
                return getDeviceInfoJson();
            }

            if (json.contains("\"action\":\"open_app\"") || json.contains("\"package\"")) {
                String pkg = extractString(json, "package");
                if (pkg.isEmpty()) pkg = extractString(json, "app");
                launchApp(pkg);
                return "{\"success\":true,\"action\":\"open_app\",\"package\":\"" + pkg + "\"}";
            }

            if (json.contains("\"action\":\"open_url\"") || json.contains("\"url\"")) {
                String url = extractString(json, "url");
                openUrl(url);
                return "{\"success\":true,\"action\":\"open_url\",\"url\":\"" + url + "\"}";
            }

            if (json.contains("\"action\":\"tap\"") || json.contains("\"tap\"")) {
                int x = extractInt(json, "x", 500);
                int y = extractInt(json, "y", 500);
                if (instance != null) {
                    instance.performTap(x, y);
                    return "{\"success\":true,\"action\":\"tap\",\"x\":" + x + ",\"y\":" + y + "}";
                } else {
                    return "{\"success\":false,\"error\":\"Accessibility required for tap\"}";
                }
            }

            if (json.contains("\"action\":\"swipe\"") || json.contains("\"swipe\"")) {
                int x1 = extractInt(json, "x1", 500);
                int y1 = extractInt(json, "y1", 1200);
                int x2 = extractInt(json, "x2", 500);
                int y2 = extractInt(json, "y2", 400);
                int dur = extractInt(json, "duration", 250);
                if (instance != null) {
                    instance.performSwipe(x1, y1, x2, y2, dur);
                    return "{\"success\":true,\"action\":\"swipe\"}";
                } else {
                    return "{\"success\":false,\"error\":\"Accessibility required for swipe\"}";
                }
            }

            if (json.contains("\"action\":\"key\"") || json.contains("\"key\"")) {
                String k = extractString(json, "key");
                if (instance != null) {
                    instance.performKey(k);
                    return "{\"success\":true,\"action\":\"key\",\"key\":\"" + k + "\"}";
                } else {
                    return "{\"success\":false,\"error\":\"Accessibility required for keys\"}";
                }
            }

            if (json.contains("\"action\":\"type\"") || json.contains("\"type\"")) {
                String text = extractString(json, "text");
                if (instance != null) {
                    instance.performType(text);
                    return "{\"success\":true,\"action\":\"type\",\"text\":\"" + text + "\"}";
                } else {
                    return "{\"success\":false,\"error\":\"Accessibility required for type\"}";
                }
            }

            return "{\"success\":true,\"message\":\"acknowledged\"}";
        } catch (Exception e) {
            return "{\"success\":false,\"error\":\"" + e.getMessage() + "\"}";
        }
    }

    public void performTap(int x, int y) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            Path path = new Path();
            path.moveTo(x, y);
            GestureDescription.Builder builder = new GestureDescription.Builder();
            builder.addStroke(new GestureDescription.StrokeDescription(path, 0, 50));
            dispatchGesture(builder.build(), null, null);
        }
    }

    public void performSwipe(int x1, int y1, int x2, int y2, int duration) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            Path path = new Path();
            path.moveTo(x1, y1);
            path.lineTo(x2, y2);
            GestureDescription.Builder builder = new GestureDescription.Builder();
            builder.addStroke(new GestureDescription.StrokeDescription(path, 0, Math.max(duration, 100)));
            dispatchGesture(builder.build(), null, null);
        }
    }

    public void performKey(String key) {
        if ("home".equalsIgnoreCase(key)) {
            performGlobalAction(GLOBAL_ACTION_HOME);
        } else if ("back".equalsIgnoreCase(key)) {
            performGlobalAction(GLOBAL_ACTION_BACK);
        } else if ("recents".equalsIgnoreCase(key) || "apps".equalsIgnoreCase(key)) {
            performGlobalAction(GLOBAL_ACTION_RECENTS);
        } else if ("notifications".equalsIgnoreCase(key)) {
            performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS);
        } else if ("lock".equalsIgnoreCase(key) && Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN);
        }
    }

    public void performType(String text) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root != null) {
            AccessibilityNodeInfo focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (focused != null) {
                Bundle args = new Bundle();
                args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text);
                focused.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
            }
        }
    }

    public static void launchApp(String packageName) {
        try {
            Context ctx = instance != null ? instance : appContext;
            if (ctx != null) {
                Intent intent = ctx.getPackageManager().getLaunchIntentForPackage(packageName);
                if (intent != null) {
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    ctx.startActivity(intent);
                }
            }
        } catch (Exception ignored) {}
    }

    public static void openUrl(String url) {
        try {
            Context ctx = instance != null ? instance : appContext;
            if (ctx != null) {
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    url = "https://" + url;
                }
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                ctx.startActivity(intent);
            }
        } catch (Exception ignored) {}
    }

    public static String getDeviceInfoJson() {
        Context ctx = instance != null ? instance : appContext;
        String ip = getIpAddress();
        int battery = getBatteryLevel(ctx);
        int w = 1080, h = 2400;
        if (ctx != null) {
            try {
                DisplayMetrics dm = ctx.getResources().getDisplayMetrics();
                w = dm.widthPixels;
                h = dm.heightPixels;
            } catch (Exception ignored) {}
        }
        boolean touch = (instance != null);
        return "{" +
                "\"success\":true," +
                "\"ip\":\"" + ip + "\"," +
                "\"port\":9090," +
                "\"model\":\"" + Build.MANUFACTURER + " " + Build.MODEL + "\"," +
                "\"android\":\"" + Build.VERSION.RELEASE + "\"," +
                "\"battery\":" + battery + "," +
                "\"width\":" + w + "," +
                "\"height\":" + h + "," +
                "\"touch_enabled\":" + touch +
                "}";
    }

    public static String getIpAddress() {
        try {
            List<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface intf : interfaces) {
                List<InetAddress> addrs = Collections.list(intf.getInetAddresses());
                for (InetAddress addr : addrs) {
                    if (!addr.isLoopbackAddress()) {
                        String sAddr = addr.getHostAddress();
                        if (sAddr.indexOf(':') < 0) {
                            return sAddr;
                        }
                    }
                }
            }
        } catch (Exception ignored) {}
        return "127.0.0.1";
    }

    private static int getBatteryLevel(Context ctx) {
        if (ctx == null) return 100;
        try {
            BatteryManager bm = (BatteryManager) ctx.getSystemService(Context.BATTERY_SERVICE);
            if (bm != null) {
                return bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
            }
        } catch (Exception ignored) {}
        return 100;
    }

    public static void registerWithMaster(final Context context) {
        if (context != null) appContext = context.getApplicationContext();
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(1500);
                    String[] possibleMasters = new String[]{"192.168.43.1", "10.141.242.56", "192.168.1.1", "10.0.2.2"};
                    for (String m : possibleMasters) {
                        try {
                            URL url = new URL("http://" + m + ":8000/api/phones/register");
                            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                            conn.setRequestMethod("POST");
                            conn.setConnectTimeout(1500);
                            conn.setReadTimeout(1500);
                            conn.setDoOutput(true);
                            conn.setRequestProperty("Content-Type", "application/json");
                            String payload = getDeviceInfoJson();
                            conn.getOutputStream().write(payload.getBytes("UTF-8"));
                            int code = conn.getResponseCode();
                            if (code == 200) break;
                        } catch (Exception ignored) {}
                    }
                } catch (Exception ignored) {}
            }
        }).start();
    }

    private static int extractInt(String json, String key, int def) {
        try {
            String p = "\"" + key + "\":";
            int idx = json.indexOf(p);
            if (idx == -1) return def;
            int start = idx + p.length();
            int end = start;
            while (end < json.length() && (Character.isDigit(json.charAt(end)) || json.charAt(end) == '-')) {
                end++;
            }
            return Integer.parseInt(json.substring(start, end).trim());
        } catch (Exception e) {
            return def;
        }
    }

    private static String extractString(String json, String key) {
        try {
            String p = "\"" + key + "\":\"";
            int idx = json.indexOf(p);
            if (idx == -1) return "";
            int start = idx + p.length();
            int end = json.indexOf("\"", start);
            if (end == -1) return "";
            return json.substring(start, end);
        } catch (Exception e) {
            return "";
        }
    }
}
