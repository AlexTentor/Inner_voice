import mido

def list_midi_ports():
    # List input ports
    print("Available MIDI Input ports:")
    for port in mido.get_input_names():
        print(f"  - {port}")
    
    print("\nAvailable MIDI Output ports:")
    # List output ports
    for port in mido.get_output_names():
        print(f"  - {port}")

if __name__ == "__main__":
    list_midi_ports()