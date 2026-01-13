import network
import socket
import time
import json
import gc

class WiFiProvisioning:
    def __init__(self, ap_ssid="FlightFrame-Setup", ap_password=""):
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.ap = network.WLAN(network.AP_IF)
        self.sta = network.WLAN(network.STA_IF)
        
    def start_ap(self):
        """Start Access Point mode"""
        self.ap.active(True)
        if self.ap_password:
            self.ap.config(essid=self.ap_ssid, password=self.ap_password, authmode=network.AUTH_WPA_WPA2_PSK)
        else:
            self.ap.config(essid=self.ap_ssid, authmode=network.AUTH_OPEN)
        
        while not self.ap.active():
            time.sleep(0.1)
        
        print(f"Access Point started:  {self.ap_ssid}")
        print(f"IP Address: {self.ap.ifconfig()[0]}")
        return self.ap. ifconfig()[0]
    
    def scan_networks(self):
        """Scan for available WiFi networks"""
        self.sta.active(True)
        networks = self.sta.scan()
        
        # Format:  (ssid, bssid, channel, RSSI, authmode, hidden)
        network_list = []
        for net in networks:
            network_list.append({
                'ssid': net[0]. decode('utf-8'),
                'rssi': net[3],
                'security': net[4] != 0  # True if secured
            })
        
        # Sort by signal strength
        network_list.sort(key=lambda x: x['rssi'], reverse=True)
        
        # Remove duplicates (keep strongest signal)
        seen = set()
        unique_networks = []
        for net in network_list:
            if net['ssid'] not in seen and net['ssid']: 
                seen.add(net['ssid'])
                unique_networks.append(net)
        
        return unique_networks
    
    def test_connection(self, ssid, password, timeout=10):
        """Test WiFi connection with given credentials"""
        self.sta.active(True)
        self.sta.disconnect()
        time.sleep(0.5)
        
        print(f"Attempting to connect to {ssid}...")
        self.sta.connect(ssid, password)
        
        start_time = time.time()
        while not self.sta.isconnected() and (time.time() - start_time) < timeout:
            time. sleep(0.5)
        
        if self. sta.isconnected():
            print(f"Successfully connected to {ssid}")
            print(f"IP Address: {self.sta.ifconfig()[0]}")
            return True
        else:
            print(f"Failed to connect to {ssid}")
            self.sta.disconnect()
            return False
    
    def save_config(self, ssid, password):
        """Save WiFi credentials to ws_config.py"""
        try:
            # Read existing config
            with open('ws_config.py', 'r') as f:
                lines = f.readlines()
            
            # Update WiFi credentials
            new_lines = []
            for line in lines:
                if line.startswith('WIFI_SSID'):
                    new_lines.append(f'WIFI_SSID = "{ssid}"\n')
                elif line. startswith('WIFI_PASSWORD'):
                    new_lines.append(f'WIFI_PASSWORD = "{password}"\n')
                else:
                    new_lines. append(line)
            
            # Write updated config
            with open('ws_config.py', 'w') as f:
                f.writelines(new_lines)
            
            print("Configuration saved successfully")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def start_web_server(self):
        """Start web server for configuration"""
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)
        
        print('Web server listening on port 80')
        
        while True:
            try:
                cl, addr = s.accept()
                print(f'Client connected from {addr}')
                
                request = cl.recv(1024).decode('utf-8')
                
                # Parse request
                request_line = request.split('\n')[0]
                path = request_line.split()[1]
                
                if path == '/': 
                    response = self.get_html_page()
                    cl.send('HTTP/1.1 200 OK\r\n')
                    cl.send('Content-Type: text/html\r\n')
                    cl. send('Connection: close\r\n\r\n')
                    cl.sendall(response)
                
                elif path == '/scan':
                    networks = self.scan_networks()
                    response = json.dumps(networks)
                    cl.send('HTTP/1.1 200 OK\r\n')
                    cl.send('Content-Type: application/json\r\n')
                    cl.send('Connection: close\r\n\r\n')
                    cl.sendall(response)
                
                elif path. startswith('/connect'):
                    # Extract POST data
                    body_start = request.find('\r\n\r\n') + 4
                    body = request[body_start:]
                    
                    try:
                        data = json. loads(body)
                        ssid = data.get('ssid')
                        password = data. get('password')
                        
                        # Test connection
                        if self. test_connection(ssid, password):
                            # Save configuration
                            self.save_config(ssid, password)
                            response = json.dumps({'success': True, 'message': 'Connected successfully'})
                        else:
                            response = json.dumps({'success': False, 'message': 'Failed to connect'})
                    except Exception as e:
                        response = json.dumps({'success': False, 'message': str(e)})
                    
                    cl.send('HTTP/1.1 200 OK\r\n')
                    cl.send('Content-Type: application/json\r\n')
                    cl.send('Connection: close\r\n\r\n')
                    cl. sendall(response)
                
                else:
                    cl.send('HTTP/1.1 404 Not Found\r\n')
                    cl.send('Connection: close\r\n\r\n')
                
                cl.close()
                gc.collect()
                
            except Exception as e:
                print(f'Error: {e}')
                try:
                    cl.close()
                except:
                    pass
    
    def get_html_page(self):
        """Return HTML page for WiFi configuration"""
        html = """<! DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlightFrame WiFi Setup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background:  linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow:  0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 30px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }
        . subtitle {
            color: #666;
            margin-bottom: 25px;
            font-size: 14px;
        }
        . section {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size:  14px;
            transition: border-color 0.3s;
        }
        select:focus, input:focus {
            outline:  none;
            border-color:  #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition:  transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform:  translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        button: active {
            transform: translateY(0);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
        }
        .status.info {
            background: #e3f2fd;
            color:  #1976d2;
            display: block;
        }
        .status.success {
            background: #e8f5e9;
            color: #388e3c;
            display:  block;
        }
        . status.error {
            background: #ffebee;
            color: #d32f2f;
            display: block;
        }
        .refresh-btn {
            background: #f5f5f5;
            color: #333;
            padding: 8px 16px;
            font-size: 12px;
            margin-top: 8px;
        }
        .refresh-btn:hover {
            background: #e0e0e0;
        }
        .network-info {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛜 FlightFrame Setup</h1>
        <p class="subtitle">Configure your WiFi connection</p>
        
        <div class="section">
            <label for="ssid">Select Network:</label>
            <select id="ssid">
                <option value="">Scanning networks...</option>
            </select>
            <button class="refresh-btn" onclick="scanNetworks()">🔄 Refresh Networks</button>
        </div>
        
        <div class="section">
            <label for="password">Password:</label>
            <input type="password" id="password" placeholder="Enter WiFi password">
        </div>
        
        <button onclick="connectWiFi()" id="connectBtn">Connect</button>
        
        <div id="status" class="status"></div>
    </div>
    
    <script>
        let networks = [];
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }
        
        async function scanNetworks() {
            showStatus('Scanning for networks... ', 'info');
            const ssidSelect = document.getElementById('ssid');
            ssidSelect.innerHTML = '<option value="">Scanning... </option>';
            
            try {
                const response = await fetch('/scan');
                networks = await response.json();
                
                ssidSelect.innerHTML = '<option value="">Select a network</option>';
                networks.forEach(net => {
                    const option = document.createElement('option');
                    option.value = net.ssid;
                    const security = net.security ? '🔒' : '🔓';
                    const signal = getSignalBars(net.rssi);
                    option.textContent = `${security} ${net.ssid} ${signal}`;
                    ssidSelect.appendChild(option);
                });
                
                showStatus(`Found ${networks.length} networks`, 'info');
            } catch (error) {
                showStatus('Error scanning networks:  ' + error, 'error');
            }
        }
        
        function getSignalBars(rssi) {
            if (rssi >= -50) return '▂▄▆█';
            if (rssi >= -60) return '▂▄▆';
            if (rssi >= -70) return '▂▄';
            return '▂';
        }
        
        async function connectWiFi() {
            const ssid = document.getElementById('ssid').value;
            const password = document.getElementById('password').value;
            const connectBtn = document.getElementById('connectBtn');
            
            if (!ssid) {
                showStatus('Please select a network', 'error');
                return;
            }
            
            connectBtn.disabled = true;
            showStatus('Connecting to ' + ssid + '... ', 'info');
            
            try {
                const response = await fetch('/connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ssid, password })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('✅ ' + result.message + '.  Device will restart... ', 'success');
                    setTimeout(() => {
                        showStatus('You can now close this page and reconnect to your main WiFi. ', 'success');
                    }, 2000);
                } else {
                    showStatus('❌ ' + result.message, 'error');
                    connectBtn.disabled = false;
                }
            } catch (error) {
                showStatus('Error:  ' + error, 'error');
                connectBtn.disabled = false;
            }
        }
        
        // Scan networks on page load
        scanNetworks();
    </script>
</body>
</html>"""
        return html


def start_provisioning():
    """Start WiFi provisioning mode"""
    provisioning = WiFiProvisioning(ap_ssid="FlightFrame-Setup", ap_password="")
    ip = provisioning.start_ap()
    print(f"\n{'='*40}")
    print("WiFi Provisioning Mode Active")
    print(f"{'='*40}")
    print(f"1. Connect to WiFi: {provisioning.ap_ssid}")
    print(f"2. Open browser: http://{ip}")
    print(f"{'='*40}\n")
    provisioning.start_web_server()
