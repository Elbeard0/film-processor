import RPi.GPIO as GPIO
import time
import threading

# GPIO Setup
GPIO.setmode(GPIO.BCM)

# Pin Configuration for Pi Zero W
SWITCH_1_PIN = 17      # Pin 11
SWITCH_2_PIN = 22      # Pin 15
RELAY_1_PIN = 23       # Pin 18
RELAY_2_PIN = 21       # Pin 40 (GPIO 24 doesn't exist on Pi Zero W)

# Setup pins
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RELAY_2_PIN, GPIO.OUT, initial=GPIO.LOW)

# State tracking
cycle_running = False
switch_1_pressed = False
switch_2_pressed = False
manual_relay_1_on = False

def relay_cycle():
    """
    Switch 1 cycle:
    - Relay 1 ON for 15 seconds
    - Relay 1 OFF for 0.5 seconds
    - Relay 2 ON for 15 seconds
    - Relay 2 OFF for 0.5 seconds
    - Repeat until stopped
    """
    global cycle_running
    
    while cycle_running:
        try:
            # Relay 1 ON for 15 seconds
            GPIO.output(RELAY_1_PIN, GPIO.HIGH)
            print("[CYCLE] Relay 1 ON (15s)")
            time.sleep(15)
            
            # Relay 1 OFF for 0.5 seconds
            GPIO.output(RELAY_1_PIN, GPIO.LOW)
            print("[CYCLE] Relay 1 OFF (0.5s)")
            time.sleep(0.5)
            
            # Relay 2 ON for 15 seconds
            GPIO.output(RELAY_2_PIN, GPIO.HIGH)
            print("[CYCLE] Relay 2 ON (15s)")
            time.sleep(15)
            
            # Relay 2 OFF for 0.5 seconds
            GPIO.output(RELAY_2_PIN, GPIO.LOW)
            print("[CYCLE] Relay 2 OFF (0.5s)")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[ERROR] Cycle error: {e}")
            break
    
    # Cleanup when cycle stops
    GPIO.output(RELAY_1_PIN, GPIO.LOW)
    GPIO.output(RELAY_2_PIN, GPIO.LOW)
    print("[CYCLE] Stopped - All relays OFF")

def main():
    global cycle_running, switch_1_pressed, switch_2_pressed, manual_relay_1_on
    
    print("=" * 60)
    print("Film Processor Relay Control - Raspberry Pi Zero W")
    print("=" * 60)
    print("Switch 1 (GPIO 17, Pin 11): Start/Stop cycle mode")
    print("  - Press: Start repeating relay sequence")
    print("  - Press again: Stop sequence")
    print("")
    print("Switch 2 (GPIO 22, Pin 15): Manual Relay 1 control")
    print("  - Press: Relay 1 ON/OFF (when cycle not running)")
    print("")
    print("Relay 1 output: GPIO 23 (Pin 18)")
    print("Relay 2 output: GPIO 21 (Pin 40)")
    print("=" * 60)
    print("")
    
    cycle_thread = None
    
    try:
        while True:
            # Read switch 1 - Cycle mode
            if GPIO.input(SWITCH_1_PIN) == GPIO.LOW and not switch_1_pressed:
                switch_1_pressed = True
                
                if not cycle_running:
                    # Start cycle
                    cycle_running = True
                    cycle_thread = threading.Thread(target=relay_cycle, daemon=True)
                    cycle_thread.start()
                    print("[SW1] Pressed: Starting cycle mode")
                else:
                    # Stop cycle
                    cycle_running = False
                    print("[SW1] Pressed: Stopping cycle mode")
                    
            elif GPIO.input(SWITCH_1_PIN) == GPIO.HIGH:
                switch_1_pressed = False
            
            # Read switch 2 - Manual relay 1 control
            if GPIO.input(SWITCH_2_PIN) == GPIO.LOW and not switch_2_pressed:
                switch_2_pressed = True
                
                if not cycle_running:  # Only allow manual control if cycle is not running
                    manual_relay_1_on = not manual_relay_1_on
                    GPIO.output(RELAY_1_PIN, GPIO.HIGH if manual_relay_1_on else GPIO.LOW)
                    
                    status = "ON" if manual_relay_1_on else "OFF"
                    print(f"[SW2] Pressed: Relay 1 {status} (manual)")
                else:
                    print("[SW2] Pressed: Cycle mode active - cannot use manual control")
                    
            elif GPIO.input(SWITCH_2_PIN) == GPIO.HIGH:
                switch_2_pressed = False
            
            time.sleep(0.05)  # Debounce delay

    except KeyboardInterrupt:
        print("\n[INFO] Shutdown requested by user")
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        
    finally:
        cycle_running = False
        GPIO.output(RELAY_1_PIN, GPIO.LOW)
        GPIO.output(RELAY_2_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("[INFO] GPIO cleaned up - Exiting")

if __name__ == "__main__":
    main()
