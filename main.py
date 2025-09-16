import serial
import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial('COM10', baudrate=115200, timeout=1)
buffer = bytearray()
header = bytearray([0xAA, 0xAB, 0xAC])
packet_size = 516  # bytes after header

# Set up matplotlib for real-time plotting
plt.ion()  # interactive mode on
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((16,16)), cmap='hot', interpolation='nearest')
plt.colorbar(heatmap)
plt.title("Real-time Heatmap")

while True:
    # Read incoming bytes
    buffer.extend(ser.read(ser.in_waiting or 1))

    # Look for header
    i = 0
    while i <= len(buffer) - len(header):
        if buffer[i:i+3] == header:
            # Check if full packet is in buffer
            if len(buffer) >= i + 3 + packet_size:
                packet_bytes = buffer[i:i+3+packet_size]

                # Convert to 16x16 array (combine two bytes per value)
                array_256 = []
                for j in range(3, 3+256*2, 2):  # 256 values, 2 bytes each
                    value = (packet_bytes[j] << 8) | packet_bytes[j+1]
                    array_256.append(value)

                array_16x16 = np.array(array_256, dtype=np.uint16).reshape((16,16))

                # Update heatmap
                heatmap.set_data(array_16x16)
                heatmap.set_clim(vmin=0, vmax=512)  # fixed color scale
                plt.pause(0.01)

                # Remove processed packet from buffer
                buffer = buffer[i+3+packet_size:]
                i = -1  # reset index
            else:
                break
        i += 1
