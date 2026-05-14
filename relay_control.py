import RPi.GPIO as GPIO
import time
import threading

# GPIO Setup
GPIO.setmode(GPIO.BCM)

# Pin Configuration for Pi Zero W
# NOTE: IO56D02-12V-001 uses ACTIVE LOW inputs
# GPIO.LOW (0V) = Relay ON (connects to GND)
# GPIO.HIGH (3.3V) = Relay OFF (disconnects from GND)

SWITCH_1_PIN = 17      # Pin 11 (Input from momentary switch)
SWITCH_2_PIN = 22      # Pin 15 (Input from momentary switch)
RELAY_1_PIN = 23       # Pin 18 (Output to IO56D02 K1 - Forward)
RELAY_2_PIN = 21       # Pin 40 (Output to IO56D02 K2 - Reverse)
ALWAYS_OFF_1_PIN = 16  # Pin 36 (Output - Always OFF)
ALWAYS_OFF_2_PIN = 20  # Pin 38 (Output - Always OFF)

# Setup pins
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Start HIGH (OFF)
GPIO.setup(RELAY_2_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Start HIGH (OFF)
GPIO.setup(ALWAYS_OFF_1_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Always HIGH (OFF)
GPIO.setup(ALWAYS_OFF_2_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Always HIGH (OFF)

# State tracking
cycle_running = False
switch_1_pressed = False
switch_2_pressed = False
manual_relay_1_on = False

def relay_cycle():
    """
    Switch 1 cycle (ACTIVE LOW - IO56D02-12V-001):
    - Relay 1 (K1) ON for 15 seconds (GPIO.LOW)
    - Relay 2 (K2) ON for 15 seconds (GPIO.LOW)
    - Repeat until stopped (no stop delay between cycles)
    
    Always-OFF outputs remain HIGH (OFF) throughout
    """
    global cycle_running
    
    while cycle_running:
        try:
            # Relay 1 (K1) ON for 15 seconds - ACTIVE LOW
            GPIO.output(RELAY_1_PIN, GPIO.LOW)
            print("[CYCLE] Relay 1 (K1) ON - 15 seconds")
            time.sleep(15)
            
            # Relay 2 (K2) ON for 15 seconds - ACTIVE LOW
            GPIO.output(RELAY_1_PIN, GPIO.HIGH)  # Turn off Relay 1
            GPIO.output(RELAY_2_PIN, GPIO.LOW)
            print("[CYCLE] Relay 2 (K2) ON - 15 seconds")
            time.sleep(15)
            
            # End of cycle - turn off Relay 2 and repeat
            GPIO.output(RELAY_2_PIN, GPIO.HIGH)
            print("[CYCLE] Cycle complete - restarting")
            
        except Exception as e:
            print(f"[ERROR] Cycle error: {e}")
            break
    
    # Cleanup when cycle stops - set all to HIGH (OFF)
    GPIO.output(RELAY_1_PIN, GPIO.HIGH)
    GPIO.output(RELAY_2_PIN, GPIO.HIGH)
    # Always-OFF pins remain HIGH
    print("[CYCLE] Stopped - All relays OFF")

def main():
    global cycle_running, switch_1_pressed, switch_2_pressed, manual_relay_1_on
    
    print("=" * 70)
    print("Film Processor Relay Control - Raspberry Pi Zero W")
    print("Motor Controller: IO56D02-12V-001 (ACTIVE LOW)")
    print("=" * 70)
    print("")
    print("Switch 1 (GPIO 17, Pin 11): Start/Stop cycle mode")
    print("  - Press: Start repeating relay sequence")
    print("  - Press again: Stop sequence")
    print("")
    print("Switch 2 (GPIO 22, Pin 15): Manual Relay 1 (K1) control")
    print("  - Press: Relay 1 ON/OFF (when cycle not running)")
    print("")
    print("Relay 1 (K1) output: GPIO 23 (Pin 18) - Forward rotation")
    print("Relay 2 (K2) output: GPIO 21 (Pin 40) - Reverse rotation")
    print("")
    print("Cycle Sequence:")
    print("  - Relay 1 ON for 15 seconds")
    print("  - Relay 2 ON for 15 seconds")
    print("  - Repeat (no delay between cycles)")
    print("")
    print("Always-OFF output 1: GPIO 16 (Pin 36) - Permanently HIGH")
    print("Always-OFF output 2: GPIO 20 (Pin 38) - Permanently HIGH")
    print("")
    print("Active Logic: LOW = ON, HIGH = OFF")
    print("=" * 70)
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
                    # ACTIVE LOW: LOW = ON, HIGH = OFF
                    GPIO.output(RELAY_1_PIN, GPIO.LOW if manual_relay_1_on else GPIO.HIGH)
                    
                    status = "ON" if manual_relay_1_on else "OFF"
                    print(f"[SW2] Pressed: Relay 1 (K1) {status} (manual)")
                else:
                    print("[SW2] Pressed: Cycle mode active - cannot use manual control")
                    
            elif GPIO.input(SWITCH_2_PIN) == GPIO.HIGH:
                switch_2_pressed = False
            
            # Always-OFF outputs remain HIGH (OFF)
            # No action needed - they stay permanently OFF
            
            time.sleep(0.05)  # Debounce delay

    except KeyboardInterrupt:
        print("\n[INFO] Shutdown requested by user")
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        
    finally:
        cycle_running = False
        # Set all outputs to HIGH (OFF state for ACTIVE LOW inputs)
        GPIO.output(RELAY_1_PIN, GPIO.HIGH)
        GPIO.output(RELAY_2_PIN, GPIO.HIGH)
        GPIO.output(ALWAYS_OFF_1_PIN, GPIO.HIGH)
        GPIO.output(ALWAYS_OFF_2_PIN, GPIO.HIGH)
        GPIO.cleanup()
        print("[INFO] GPIO cleaned up - Exiting")

if __name__ == "__main__":
    main()
