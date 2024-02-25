import digitalio
import board
import usb_hid
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led_b = digitalio.DigitalInOut(board.GP0)
led_b.direction = digitalio.Direction.OUTPUT
led_g = digitalio.DigitalInOut(board.GP1)
led_g.direction = digitalio.Direction.OUTPUT

print("Raspberry Pi Pico multi-function knob (DiY Projects Lab)")

SW_PIN = board.GP2
DT_PIN = board.GP3
CLK_PIN = board.GP4
EXT_1 = board.GP14
EXT_2 = board.GP15

clk_last = None
count = 0
totalMode = 4
currentMode = 0

cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

clk = digitalio.DigitalInOut(CLK_PIN)
clk.direction = digitalio.Direction.INPUT

dt = digitalio.DigitalInOut(DT_PIN)
dt.direction = digitalio.Direction.INPUT

sw = digitalio.DigitalInOut(SW_PIN)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP

sw1 = digitalio.DigitalInOut(EXT_1)
sw1.direction = digitalio.Direction.INPUT
sw1.pull = digitalio.Pull.UP

sw2 = digitalio.DigitalInOut(EXT_2)
sw2.direction = digitalio.Direction.INPUT
sw2.pull = digitalio.Pull.UP

def millis():
    return time.monotonic() * 1000

def toggle_led(state):
    led.value = state

def ccw():
    print("CCW")

    if currentMode == 0:  # Mac brightness down
        mouse.move(0, -10, 0)

    elif currentMode == 1:  # Mac horizontal scroll right
        mouse.move(wheel=1)

    elif currentMode == 2:  # Volume decrement
        mouse.move(-10, 0, 0)
        
    elif currentMode == 3:
          keyboard.send(Keycode.LEFT_ARROW)

def cw():
    print("CW")
    if currentMode == 0:  # Windows brightness up
        mouse.move(0, 10, 0)

    elif currentMode == 1:  # Mac horizontal scroll left
        mouse.move(wheel=-1)

    elif currentMode == 2:  # Volume increment
        mouse.move(10, 0, 0)
        
    elif currentMode == 3:
          keyboard.send(Keycode.RIGHT_ARROW)

def long_press():
    # Mac sleep: CMD + OPT + EJECT
    mouse.press(Mouse.MIDDLE_BUTTON)
    cc.send(ConsumerControlCode.EJECT)
    keyboard.release_all()

# Define LED blinking state machine
blink_state = False
blink_duration = 0.5  # Initial blink duration
last_blink_time = millis()

# Define blink rates for each mode (blinks per second)
blink_rates = [1, 5, 7, 9]  # Adjust as needed for each mode

while True:
    clkState = clk.value
    if clk_last != clkState:
        if dt.value != clkState:
            cw()
        else:
            ccw()
    if sw.value == 0:
        pressTime = millis()
        time.sleep(0.2)
        longPress = False
        mouse.release_all()
        while sw.value == 0:
            if millis() - pressTime > 1000 and not longPress:
                print("longPress")
                longPress = True
                long_press()

        if not longPress:
            mouse.release_all()
            currentMode += 1
            currentMode %= totalMode
            print("Mode: " + str(currentMode))
            
            # Change the blink duration based on the new mode
            blink_duration = 1 / blink_rates[currentMode]  # Update blink duration for the mode
     
    if currentMode==0:
        led_b.value=1
        led_g.value=1
    elif currentMode==1:
        led_b.value=1
        led_g.value=0
    elif currentMode==2:
        led_b.value=0
        led_g.value=1
    elif currentMode==3:
        # Adjust LED behavior for mode 3 if needed
        led_b.value=0
        led_g.value=0  #
    if sw1.value == 0:        
        print("EXTERNAL 1")
        keyboard.press(Keycode.CONTROL)
        
    if sw2.value == 0:
        pressTime = millis()
        time.sleep(0.2)
        keyboard.press(Keycode.CONTROL, Keycode.C)
        print("EXTERNAL 2")
    else:
        keyboard.release_all();
      
    # Update LED state based on the blink state machine
    now = millis()
    if now - last_blink_time >= blink_duration * 1000:
        toggle_led(not blink_state)
        blink_state = not blink_state
        last_blink_time = now
    
    clk_last = clkState
