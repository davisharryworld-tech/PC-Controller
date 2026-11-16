package com.personalai.agent;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // Automatically start the background Port 9090 Server upon phone reboot
        AgentAccessibilityService.startServer(context);
        AgentAccessibilityService.registerWithMaster(context);
    }
}
