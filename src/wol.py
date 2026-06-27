import socket
import struct
import time
import urllib.request
import urllib.error

def is_ollama_ready(api_url, timeout=2):
    """Checks if Ollama is responding on the given API URL."""
    try:
        req = urllib.request.Request(f"{api_url}/api/tags")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False

def send_wol_packet(mac_address):
    """Sends a Wake-on-LAN magic packet to the specified MAC address."""
    print(f"[WOL] Sending Wake-on-LAN packet to {mac_address}...")
    try:
        # Parse MAC address
        add_oct = mac_address.split(':')
        if len(add_oct) != 6:
            raise ValueError("Invalid MAC address format. Expected XX:XX:XX:XX:XX:XX")
        
        hwa = struct.pack('BBBBBB', 
                          int(add_oct[0], 16),
                          int(add_oct[1], 16),
                          int(add_oct[2], 16),
                          int(add_oct[3], 16),
                          int(add_oct[4], 16),
                          int(add_oct[5], 16))
        
        # Build magic packet
        msg = b'\xff' * 6 + hwa * 16
        
        # Broadcast UDP packet
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Send broadcast to standard port 9 and subnetwork broadcasts
        soc.sendto(msg, ('255.255.255.255', 9))
        soc.sendto(msg, ('255.255.255.255', 7))
        soc.close()
        print("[WOL] Magic packet sent successfully.")
        return True
    except Exception as e:
        print(f"[WOL] Failed to send magic packet: {e}")
        return False

def ensure_ryzen_awake(api_url, mac_address, ip_address=None, max_wait_sec=60):
    """
    Checks if Ollama is responsive. If not, sends a WOL packet to the Ryzen node
    and waits until Ollama starts responding or max_wait_sec is reached.
    """
    if is_ollama_ready(api_url):
        print("[WOL] Ollama is already awake and responsive.")
        return True

    print("[WOL] Ollama is unresponsive. Attempting to wake the Ryzen node...")
    send_wol_packet(mac_address)

    # Wait for the node to wake up and the port tunnel to establish
    start_time = time.time()
    check_interval = 3
    
    while time.time() - start_time < max_wait_sec:
        print(f"[WOL] Waiting for Ollama to wake up ({int(time.time() - start_time)}s elapsed)...")
        time.sleep(check_interval)
        if is_ollama_ready(api_url):
            print(f"[WOL] Ollama is now responsive after {int(time.time() - start_time)} seconds!")
            return True
            
    print(f"[WOL] Warning: Ollama did not respond within {max_wait_sec} seconds.")
    return False
