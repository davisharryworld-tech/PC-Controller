import asyncio
import json
import sys
import requests
import websockets

HTTP_BASE = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/controller"


def test_health_endpoint():
    print("\n[1/3] Testing Health Endpoint (GET /health)...")
    try:
        resp = requests.get(f"{HTTP_BASE}/health", timeout=5)
        print(f"  -> HTTP Status: {resp.status_code}")
        data = resp.json()
        print(f"  -> Response: {json.dumps(data, indent=2)}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert data.get("status") == "online", "Status is not 'online'"
        assert "local_ip" in data, "local_ip missing from response"
        print("  [SUCCESS] Health endpoint verified!")
        return data
    except Exception as e:
        print(f"  [FAILED] Health check failed: {e}")
        raise


def test_system_info_endpoint():
    print("\n[2/3] Testing System Info Endpoint (GET /api/system)...")
    try:
        resp = requests.get(f"{HTTP_BASE}/api/system", timeout=5)
        print(f"  -> HTTP Status: {resp.status_code}")
        data = resp.json()
        print(f"  -> Response: {json.dumps(data, indent=2)}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert "cpu_model" in data, "cpu_model missing"
        print("  [SUCCESS] System info endpoint verified!")
        return data
    except Exception as e:
        print(f"  [FAILED] System info check failed: {e}")
        raise


async def test_websocket():
    print(f"\n[3/3] Testing WebSocket Connection ({WS_URL})...")
    try:
        async with websockets.connect(WS_URL) as ws:
            # 1. Receive welcome message
            welcome_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            welcome_msg = json.loads(welcome_raw)
            print(f"  -> Received Welcome: {welcome_msg}")
            assert welcome_msg.get("type") == "welcome", "Did not receive welcome message"

            # 2. Test Ping / Pong
            print("  -> Sending Ping...")
            ping_msg = {"type": "ping", "timestamp": "2026-11-04T00:00:00Z"}
            await ws.send(json.dumps(ping_msg))
            pong_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            pong_msg = json.loads(pong_raw)
            print(f"  -> Received: {pong_msg}")
            assert pong_msg.get("type") == "pong", f"Expected pong, got {pong_msg}"

            # 3. Test Mobile Handshake
            print("  -> Sending Android Device Handshake...")
            handshake_msg = {
                "type": "handshake",
                "device_id": "test_android_phone_001",
                "payload": {"device_name": "Test Android Mobile"},
            }
            await ws.send(json.dumps(handshake_msg))
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack_msg = json.loads(ack_raw)
            print(f"  -> Received: {ack_msg}")
            assert ack_msg.get("type") == "handshake_ack", f"Expected handshake_ack, got {ack_msg}"

            # 4. Test Status Query
            print("  -> Sending Status Query...")
            status_msg = {"type": "status"}
            await ws.send(json.dumps(status_msg))
            status_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            status_resp = json.loads(status_raw)
            print(f"  -> Received: {status_resp}")
            assert status_resp.get("type") == "status", f"Expected status response, got {status_resp}"

            print("  [SUCCESS] WebSocket bidirectional communication verified!")
    except Exception as e:
        print(f"  [FAILED] WebSocket test failed: {e}")
        raise


def run_all_tests():
    print("=" * 60)
    print("RUNNING VERIFICATION SUITE FOR PC CONTROLLER AGENT")
    print("=" * 60)
    test_health_endpoint()
    test_system_info_endpoint()
    asyncio.run(test_websocket())
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

