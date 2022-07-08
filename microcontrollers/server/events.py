from typing import Optional


class Event:
    CODE: bytes


# Joystick event examples
# b"j100:-52:0"
# b"j0:100:1"
# b"j-1:5:1"
class JoystickPositionUpdatedEvent(Event):
    CODE = b"j"

    def __init__(self, new_x: int, new_y: int, button_pressed: bool):
        self.new_x = new_x
        self.new_y = new_y
        self.button_pressed = button_pressed
    
    def __str__(self):
        return "JoystickPositionUpdatedEvent(new_x={}, new_y={}, button_pressed={})".format(self.new_x, self.new_y, self.button_pressed)

    @staticmethod
    def decode(data: bytes) -> Optional["JoystickPositionUpdatedEvent"]:
        parts = data.decode("ascii", "ignore").split(":")

        if len(parts) != 3:
            return None
        
        try:
            new_x = int(parts[0])
            new_y = int(parts[1])
            btn_int = int(parts[2])
        except ValueError:
            return None
        
        if new_x < -100 or new_x > 100:
            return None
        
        if new_y < -100 or new_y > 100:
            return None

        if btn_int != 0 and btn_int != 1:
            return None
        
        return JoystickPositionUpdatedEvent(new_x, new_y, btn_int == 1)

    def encode(self) -> bytes:
        return "{}:{}:{}".format(self.new_x, self.new_y, self.button_pressed).encode("ascii")


# Parses event from bytes
# Returns None if event code or its data are invalid
# Format of data:
# 1st byte - code of the event
# other bytes - data of the event
def decode_event(data: bytes) -> Optional[Event]:
    if not data:
        return None

    code = data[0]

    if code == JoystickPositionUpdatedEvent.CODE:
        return JoystickPositionUpdatedEvent.decode(data[1:])

    return None

def encode_event(event: Event) -> bytes:
    return chr(event.CODE) + event.encode()
