from machine import Pin, PWM
import network
import socketc
import sys
import time

def cleanup():
    """Fungsi untuk membersihkan semua resource"""
    print("\n Cleaning up...")
    # Stop semua motor
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    # Matikan LED
    LED.duty(0)
    # Matikan WiFi
    try:
        ap.active(False)
        print("✓ WiFi disabled")
    except:
        pass
    # Tutup socket
    try:
        s.close()
        print("✓ Socket closed")
    except:
        pass

def start_countdown():
    """Countdown 5 detik dengan opsi cancel"""
    print("\n" + "="*50)
    print("ESP32 RC Car")
    print("="*50)
    print("Starting in 5 seconds...")
    print("Press Ctrl+C to cancel")
    print("="*50)
    
    try:
        for i in range(5, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        return True  # Lanjut ke main program
    except KeyboardInterrupt:
        print("\n❌ Cancelled! Press Ctrl+C again to exit completely")
        return False  # Kembali ke awal

# ========== Setup Motor Pins ==========
IN1 = Pin(16, Pin.OUT) #oren
IN2 = Pin(26, Pin.OUT) #merah
IN3 = Pin(27, Pin.OUT) #coklat terang
IN4 = Pin(13, Pin.OUT) #kuning

# ========== Setup LED Pin ==========
LED = PWM(Pin(21), freq=1000)  # dengan PWM untuk brightness control
LED.duty(0)  # Mulai dengan LED mati
led_brightness = 1023  # Maksimal (0-1023, 1023 = paling terang)

# ========== Fungsi Kontrol Motor ==========
def maju():
    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)

def mundur():
    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)

def kiri():
    IN1.value(0)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)

def kanan():
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)

def stop():
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)

stop()

# ========== Fungsi Kontrol LED ==========
def led_on():
    LED.duty(led_brightness)

def led_off():
    LED.duty(0)

def set_brightness(level):
    global led_brightness
    # level: 1 (redup) sampai 10 (terang)
    led_brightness = int((level / 10) * 1023)
    if LED.duty() > 0:  # Jika LED nyala, update brightness
        LED.duty(led_brightness)

# ========== HTML ==========
html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="UTF-8">
<title>RC Car</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
}
.container {
    text-align: center;
    width: 100%;
    max-width: 400px;
}
h1 {
    font-size: 2.5em;
    margin-bottom: 30px;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.control-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 30px 0;
}
button {
    background: rgba(255,255,255,0.9);
    border: none;
    border-radius: 20px;
    padding: 0;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    overflow: hidden;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}
button:active {
    transform: scale(0.95);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.btn-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 35px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.btn-icon {
    font-size: 4em;
}
#forward { grid-column: 2; }
#left { grid-column: 1; grid-row: 2; }
#ledBtn { grid-column: 2; grid-row: 2; }
#right { grid-column: 3; grid-row: 2; }
#backward { grid-column: 2; grid-row: 3; }
.led-on {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
}
.led-off {
    background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
    opacity: 0.6;
}
.info {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
    color: white;
    font-size: 0.95em;
    line-height: 1.8;
}
@media (max-width: 480px) {
    h1 { font-size: 2em; }
    .btn-content { padding: 30px 15px; }
    .btn-icon { font-size: 3em; }
}
</style>
</head>
<body>
<div class="container">
    <h1>🚗 RC Car Control</h1>
    
    <div class="control-grid">
        <button id="forward" ontouchstart="cmd('F')" ontouchend="cmd('S')" 
                onmousedown="cmd('F')" onmouseup="cmd('S')">
            <div class="btn-content">
                <div class="btn-icon"></div>
            </div>
        </button>
        
        <button id="left" ontouchstart="cmd('L')" ontouchend="cmd('S')"
                onmousedown="cmd('L')" onmouseup="cmd('S')">
            <div class="btn-content">
                <div class="btn-icon"></div>
            </div>
        </button>
        
        <button id="ledBtn" ontouchstart="toggleLED()" onclick="toggleLED()">
            <div class="btn-content" id="ledContent">
                <div class="btn-icon"></div>
            </div>
        </button>
        
        <button id="right" ontouchstart="cmd('R')" ontouchend="cmd('S')"
                onmousedown="cmd('R')" onmouseup="cmd('S')">
            <div class="btn-content">
                <div class="btn-icon"></div>
            </div>
        </button>
        
        <button id="backward" ontouchstart="cmd('B')" ontouchend="cmd('S')"
                onmousedown="cmd('B')" onmouseup="cmd('S')">
            <div class="btn-content">
                <div class="btn-icon"></div>
            </div>
        </button>
    </div>
    
    <div class="info">
        Tekan dan tahan tombol untuk menggerakkan RC Car
    </div>
</div>
    
<script>
function cmd(c) {
    fetch('/' + c).catch(e => console.log(e));
}

let ledState = false;

function toggleLED() {
    ledState = !ledState;
    const content = document.getElementById('ledContent');
    
    if (ledState) {
        fetch('/LED_ON').catch(e => console.log(e));
        content.classList.remove('led-off');
        content.classList.add('led-on');
    } else {
        fetch('/LED_OFF').catch(e => console.log(e));
        content.classList.remove('led-on');
        content.classList.add('led-off');
    }
}

// Set initial state
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('ledContent').classList.add('led-off');
});
</script>
</body>
</html>
"""

# ========== MAIN PROGRAM LOOP ==========
exit_program = False  # Flag untuk exit

while True:
    # Tampilkan countdown, jika dibatalkan kembali ke sini
    try:
        if not start_countdown():
            time.sleep(2)
            continue
    except KeyboardInterrupt:
        # Double Ctrl+C saat countdown = EXIT COMPLETELY
        print("\n\nEXITING PROGRAM...")
        cleanup()
        print("✓ Program terminated")
        sys.exit(0)  # EXIT PROGRAM
    
    # Setup WiFi
    print("\n[✓] Starting WiFi...")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='RC_Car', password='12345678')
    print("[✓] WiFi: RC_Car | Pass: 12345678")
    print("[✓] IP:", ap.ifconfig()[0])

    # Setup Web Server
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    s.settimeout(3)
    print("[✓] Server ready")

    print("\n" + "="*50)
    print("Buka: http://192.168.4.1")
    print("Press Ctrl+C to stop and restart")
    print("Press Ctrl+C twice to exit completely")
    print("="*50 + "\n")

    try:
        # Loop server utama
        while True:
            try:
                cl, addr = s.accept()
            except OSError:
                continue

            req = cl.recv(1024).decode()
            cmd = req.split()[1] if len(req.split()) > 1 else '/'

            if cmd == '/F':
                maju()
            elif cmd == '/B':
                mundur()
            elif cmd == '/L':
                kiri()
            elif cmd == '/R':
                kanan()
            elif cmd == '/S':
                stop()
            elif cmd == '/LED_ON':
                led_on()
            elif cmd == '/LED_OFF':
                led_off()

            if cmd == '/':
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                cl.sendall(html)
            else:
                cl.send("HTTP/1.1 200 OK\r\n\r\nOK")

            cl.close()

    except KeyboardInterrupt:
        print("\n\nServer stopping...")
        cleanup()
        print("\n" + "="*50)
        print("Press Ctrl+C again within 3 seconds to EXIT")
        print("atau tunggu restrat dan looping awal...")
        print("="*50)
        
        # Tunggu 3 detik untuk Ctrl+C kedua
        try:
            time.sleep(3)
            print("\nRestarting...\n")
            continue
        except KeyboardInterrupt:
            # Double Ctrl+C = EXIT
            print("\n\nKELUAR PROGRAM...")
            cleanup()
            print("✓ Program BEREHENTI")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        cleanup()
        time.sleep(2)
        continue
