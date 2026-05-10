# Wiring Diagram - Raspberry Pi Zero W
## Film Processor Relay Control System

### Pi Zero W GPIO Pin Reference
```
         +3V3  1  2  +5V
GPIO 2   SDA   3  4  +5V
GPIO 3   SCL   5  6  GND
GPIO 4        7  8  GPIO 14 (TX)
        GND   9 10  GPIO 15 (RX)
GPIO 17      11 12  GPIO 18
GPIO 27      13 14  GND
GPIO 22      15 16  GPIO 23
        +3V3 17 18  GPIO 24
GPIO 10 MOSI 19 20  GND
GPIO 9  MISO 21 22  GPIO 25
GPIO 11 SCLK 23 24  GPIO 8 (CE0)
        GND  25 26  GPIO 7 (CE1)
GPIO 0  ID   27 28  GPIO 1  ID
GPIO 5       29 30  GND
GPIO 6       31 32  GPIO 12
GPIO 13      33 34  GND
GPIO 19      35 36  GPIO 16
GPIO 26      37 38  GPIO 20
        GND  39 40  GPIO 21
```

### Component List
- Raspberry Pi Zero W
- 2x Momentary Push Buttons (normally open)
- 2x 10kΩ Resistors (debouncing)
- 2-Channel Relay Module (5V) - **RECOMMENDED**
  - OR individual relays + NPN transistors (2N2222/BC547)
- Jumper wires (various)
- Power supply: 5V 2A+ (for relays)

### Pin Assignments
| Component | Pi Zero W Pin | GPIO # |
|-----------|--------------|--------|
| Switch 1  | Pin 11       | GPIO 17 |
| Switch 2  | Pin 15       | GPIO 22 |
| Relay 1   | Pin 18       | GPIO 23 |
| Relay 2   | Pin 40       | GPIO 21 |

---

## Wiring Configuration

### Option 1: Using 2-Channel Relay Module (EASIEST)

```
RELAY MODULE CONNECTIONS:
┌─────────────────────┐
│ 2-Channel Relay     │
│ ┌─────────────────┐ │
│ │ VCC  GND  IN1 IN2 │
│ └─────────────────┘ │
│      │    │   │  │   │
└──────┼────┼───┼──┼───┘
       │    │   │  │
       │    │   │  └─→ GPIO 21 (Relay 2)
       │    │   └────→ GPIO 23 (Relay 1)
       │    └────────→ GND (Pi Zero W Pin 39)
       └─────────────→ +5V Power Supply

Pi Zero W Connections:
GND (Pin 39) → Relay Module GND
GPIO 23 (Pin 18) → Relay Module IN1
GPIO 21 (Pin 40) → Relay Module IN2
+5V Power Supply → Relay Module VCC
```

### Option 2: Individual Relays + NPN Transistor (DIY)

```
RELAY 1 CIRCUIT:
GPIO 23 (Pin 18) ──[1kΩ resistor]──→ NPN Transistor Base
                                     (2N2222/BC547)
                    Collector ──→ Relay Coil + pin
                    Emitter ───→ GND
                    
Relay Common ──→ +5V Power
Relay NO (Normally Open) ──→ Load
Relay COM ──→ Relay Coil Ground

Add 1N4007 diode across relay coil (cathode to +5V, anode to GND)
to prevent back-EMF damage to transistor.

RELAY 2 CIRCUIT:
Same configuration with GPIO 21 (Pin 40) and second transistor
```

### Momentary Switch Wiring (Both Options)

```
SWITCH 1 CIRCUIT:
+5V ──→ Momentary Button ──→ 10kΩ Resistor ──→ GND
                    └──→ GPIO 17 (Pin 11) [Connect between button and resistor]

SWITCH 2 CIRCUIT:
+5V ──→ Momentary Button ──→ 10kΩ Resistor ──→ GND
                    └──→ GPIO 22 (Pin 15) [Connect between button and resistor]
```

---

## Power Supply Considerations

**Pi Zero W Power:**
- Typical draw: 150-200mA
- Via micro-USB or GPIO pin

**Relay Module Power:**
- Typical draw: 100mA per relay (when energized)
- **IMPORTANT:** Use separate 5V power supply for relays
- Do NOT power relays from Pi Zero W USB port (insufficient current)
- Recommended: 5V 2A+ dedicated power supply

**Ground Connection:**
- Connect all grounds together (Pi Zero W GND to Power Supply GND to Relay Module GND)
- This ensures common reference for all circuits

---

## Pinout Summary for Quick Reference

```
Pi Zero W Pin 11 ──→ GPIO 17 ──→ Switch 1 Input
Pi Zero W Pin 15 ──→ GPIO 22 ──→ Switch 2 Input
Pi Zero W Pin 18 ──→ GPIO 23 ──→ Relay 1 Output
Pi Zero W Pin 40 ──→ GPIO 21 ──→ Relay 2 Output
Pi Zero W Pin 39 ──→ GND ──────→ Ground (all circuits)
```

---

## Assembly Steps

1. **Prepare Relay Module** (if using Option 1)
   - Solder or connect jumper wires to VCC, GND, IN1, IN2

2. **Connect Relay Module**
   - VCC → +5V Power Supply
   - GND → Common Ground (Pi, Power Supply)
   - IN1 → GPIO 23 (Pin 18)
   - IN2 → GPIO 21 (Pin 40)

3. **Connect Switches**
   - Connect momentary buttons with pull-down resistors
   - Switch 1 → GPIO 17 (Pin 11)
   - Switch 2 → GPIO 22 (Pin 15)

4. **Connect Power**
   - +5V Power Supply to Relay Module
   - Pi Zero W USB or GPIO 5V to Pi

5. **Connect Ground**
   - All GND together

---

## Testing

```bash
# SSH into Pi Zero W
ssh pi@<ip-address>

# Navigate to project directory
cd ~/film-processor

# Run the relay control script
sudo python3 relay_control.py
```

Watch the GPIO pins with a multimeter or LED to verify switching:
- Pin 18 (GPIO 23): Should toggle when Relay 1 cycles
- Pin 40 (GPIO 21): Should toggle when Relay 2 cycles
- Pin 11 (GPIO 17): Reads switch 1 state
- Pin 15 (GPIO 22): Reads switch 2 state

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Relays not activating | Check +5V power supply to relay module, verify GPIO pins are correct |
| Switches not working | Check pull-down resistors, verify GPIO 17/22 connections |
| Pi Zero W resets when relay activates | Insufficient power supply, add capacitor (100µF) across power/GND |
| GPIO pins getting hot | Check for shorts, reduce load, verify transistor connections (if DIY) |

---

## Safety Notes

- Always use a separate power supply for relays (do NOT rely on Pi USB power)
- Add a protective diode across relay coils (1N4007)
- Use fused power supply for safety
- Keep wiring organized and away from moving parts
- Test with low-power loads before connecting high-power devices
