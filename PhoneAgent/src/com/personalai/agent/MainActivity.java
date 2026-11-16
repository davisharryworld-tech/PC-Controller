package com.personalai.agent;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.util.Collections;
import java.util.List;

public class MainActivity extends Activity {

    private TextView tvIpAddress;
    private TextView tvStatus;
    private Button btnEnableService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvIpAddress = findViewById(R.id.tvIpAddress);
        tvStatus = findViewById(R.id.tvStatus);
        btnEnableService = findViewById(R.id.btnEnableService);

        btnEnableService.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestBatteryExemption();
                Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
            }
        });

        requestBatteryExemption();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateUiState();
    }

    private void updateUiState() {
        String ip = getIpAddress();
        tvIpAddress.setText("IP: " + ip + " (Port: 9090)");

        if (AgentAccessibilityService.isServiceRunning) {
            tvStatus.setText("Status: ACTIVE & LISTENING (ON)");
            tvStatus.setTextColor(0xFF10B981);
            btnEnableService.setText("[OK] Service Active (24/7 Ready)");
            btnEnableService.setEnabled(false);
            btnEnableService.setBackgroundColor(0xFF059669);
        } else {
            tvStatus.setText("Status: Service Disabled (Waiting)");
            tvStatus.setTextColor(0xFFF87171);
            btnEnableService.setText("Enable Remote Service");
            btnEnableService.setEnabled(true);
            btnEnableService.setBackgroundColor(0xFF4F46E5);
        }
    }

    private void requestBatteryExemption() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
                if (pm != null && !pm.isIgnoringBatteryOptimizations(getPackageName())) {
                    Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                    intent.setData(Uri.parse("package:" + getPackageName()));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);
                }
            } catch (Exception ignored) {}
        }
    }

    private String getIpAddress() {
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
}
