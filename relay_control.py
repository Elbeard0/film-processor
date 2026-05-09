import RPi.GPIO as GPIO
import time
import threading

# GPIO Setup
GPIO.setmode(GPIO.BCM)

# Pin Configuration
SWITCH_1_PIN = 17
SWITCH_2_PIN = 22
RELAY_1_PIN = 23
RELAY_2_PIN = 24

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
    """Switch 1 cycle: Relay1 ON 15s, OFF 0.5s, Relay2 ON 15s, OFF 0.5s, repeat"""
    global cycle_running
    
    while cycle_running:
        # Relay 1 ON for 15 seconds
        GPIO.output(RELAY_1_PIN, GPIO.HIGH)
        print("Relay 1 ON (15s)")
        time.sleep(15)
        
        # Relay 1 OFF for 0.5 seconds
        GPIO.output(RELAY_1_PIN, GPIO.LOW)
        print("Relay 1 OFF (0.5s)")
        time.sleep(0.5)
        
        # Relay 2 ON for 15 seconds
        GPIO.output(RELAY_2_PIN, GPIO.HIGH)
        print("Relay 2 ON (15s)")
        time.sleep(15)
        
        # Relay 2 OFF for 0.5 seconds
        GPIO.output(RELAY_2_PIN, GPIO.LOW)
        print("Relay 2 OFF (0.5s)")
        time.sleep(0.5)
    
    # Cleanup when cycle stops
    GPIO.output(RELAY_1_PIN, GPIO.LOW)
    GPIO.output(RELAY_2_PIN, GPIO.LOW)
    print("Cycle stopped - All relays OFF")

try:
    print("Film Processor Relay Control Started")
    print("Switch 1 (GPIO 17): Cycle mode")
    print("Switch 2 (GPIO 22): Manual Relay 1 control")
    print()
    
    cycle_thread = None
    
    while True:
        # Read switch 1 - Cycle mode
        if GPIO.input(SWITCH_1_PIN) == GPIO.LOW and not switch_1_pressed:
            switch_1_pressed = True
            
            if not cycle_running:
                # Start cycle
                cycle_running = True
                cycle_thread = threading.Thread(target=relay_cycle, daemon=True)
                cycle_thread.start()
                print("Switch 1 pressed: Starting cycle mode")
            else:
                # Stop cycle
                cycle_running = False
                print("Switch 1 pressed: Stopping cycle mode")
                
        elif GPIO.input(SWITCH_1_PIN) == GPIO.HIGH:
            switch_1_pressed = False
        
        # Read switch 2 - Manual relay 1 control
        if GPIO.input(SWITCH_2_PIN) == GPIO.LOW and not switch_2_pressed:
            switch_2_pressed = True
            
            if not cycle_running:  # Only allow manual control if cycle is not running
                manual_relay_1_on = not manual_relay_1_on
                GPIO.output(RELAY_1_PIN, GPIO.HIGH if manual_relay_1_on else GPIO.LOW)
                
                if manual_relay_1_on:
                    print("Switch 2 pressed: Relay 1 ON (manual)")
                else:
                    print("Switch 2 pressed: Relay 1 OFF (manual)")
            else:
                print("Switch 2: Cycle mode active - cannot use manual control")
                
        elif GPIO.input(SWITCH_2_PIN) == GPIO.HIGH:
            switch_2_pressed = False
        
        time.sleep(0.05)  # Debounce delay

except KeyboardInterrupt:
    print("\nShutdown requested")
    
finally:
    cycle_running = False
    GPIO.cleanup()
    print("GPIO cleaned up - Exiting")
