# Networks Assignment 2
# Erik Macik
#

import os
import socket
import sys
import _thread # uncommented
import time
import string
from typing import Protocol
import packet
from packet import extract
import udt
import random
from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
base = 0 # uncommented
end = 0
mutex = _thread.allocate_lock() # uncommented
timer = Timer(TIMEOUT_INTERVAL) # uncommented

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str

# Get specified number of bytes of data from file to send
def generate_payload_from_file(opened_file, length=PACKET_SIZE):
    return opened_file.read(length)

# Get all packets from a file along with an ending packet
def get_packets_from_file(filename, packet_size=PACKET_SIZE):
    packets = []
    file = open(filename, "r")
    file_size = os.path.getsize(filename)
    seq = 0

    # Create a list of packet of size packet_size from file
    while file_size > 0:
        data = generate_payload_from_file(file, packet_size).encode()
        file_size -= packet_size
        pkt = packet.make(seq, data)
        packets.append(pkt)
        print("Created packet seq#", seq)
        seq += 1
    end = packet.make(len(packets), "END".encode())
    packets.append(end)
    return packets


# Send packets from file using Stop_n_wait protocol
def send_snw(sock, filename, packet_size=PACKET_SIZE):
    global base

    # Get all packets from file
    packets = get_packets_from_file(filename)
    
    # Start thread to listen for acks from receiver
    _thread.start_new_thread(receive_snw, (sock, ))

    # Send each packet
    while base < len(packets):
        # base is only incremented by the thread listening for acks
        pkt = packets[base]
        print("Sending seq# ", base, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)
        timer.start()

        # loop while the timer is running
        while timer.running():
            # if it timeed out, resend the packet
            if timer.timeout():
                timer.stop()

# Send packets from file using GBN protocol
def send_gbn(sock, filename, window_size=WINDOW_SIZE):
    global base
    global end
    # Get all packets from file
    packets = get_packets_from_file(filename)
    
    # Start thread to listen for acks from receiver
    _thread.start_new_thread(receive_gbn, (sock, ))

    # Send each packet
    while base < len(packets):
        # Sed packets sequentially in our window and start timer
        if end - base < window_size and end < len(packets):
            pkt = packets[end]
            print("Sending packet#", end, "\n")
            udt.send(pkt, sock, RECEIVER_ADDR)
            timer.stop()
            timer.start()
            end += 1

        # If the timer times out, resend everything in the window.
        if timer.timeout():
            temp_seq = base
            print("Timeout, resending window...")
            timer.stop()
            # Resend packets in window
            while temp_seq < end:
                pkt = packets[temp_seq]
                print("RESENDING packet#", temp_seq, "\n")
                udt.send(pkt, sock, RECEIVER_ADDR)
                temp_seq += 1
            # Set the timer again now that we resent everything in the window
            timer.start()

# Receive thread for stop-n-wait. If we receive an ack for a packet we
# just sent, increase base value
def receive_snw(sock):#, pkt):
    global base
    print("Entered receive_snw()")
    try:
        while True:
            print("listening for acks")

            # wait for an ack to come in
            packet, addr = udt.recv(sock)
            recv_seq_num, data = extract(packet)
            if recv_seq_num == base:
                # increase base if it is the ACK I expect
                print("Received good ACK#", recv_seq_num)
                base = recv_seq_num + 1
            else:
                # Ignore if it's a bad/repeat ACK
                print("Received bad ACK#", recv_seq_num)
    except Exception as e:
        # Exception caught when socket is closed by main thread
        print("The socket was closed.")

# Receive thread for GBN. Update base and reset the timer every time we receive an ack.
def receive_gbn(sock):
    # Fill here to handle acks
    global base
    global end
    print("Entered receive_gbn()")
    try:
        # continually receive
        while True:
            print("Listening for acks")
            packet, addr = udt.recv(sock)
            recv_seq_num, data = extract(packet)
            
            # Update base when we receive an ACK
            base = recv_seq_num + 1

            # Reset timer since we just received
            timer.stop()
            timer.start()
    except Exception as e:
        # Exception caught when socket is closed by main thread
        print("The socket was closed.")

# Main function
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Expected protocol and filename as command line argument')
        print('Usage: <-snw|-gbn> <filename>')
        exit()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    # Protocol to use and file to read from
    protocol = sys.argv[1]
    filename = sys.argv[2]

    if protocol == '-snw':
        # Send the data in this file with stop-n-wait protocol
        print('Using stop n wait')
        send_snw(sock, filename)
    elif protocol == '-gbn':
        # Send the data in this file with go-back-n protocol
        print('uisng go back n')
        send_gbn(sock, filename)
    else:
        print('Bad protocol, use one of these: <-snw|-gbn>')

    # close the socket after sending
    sock.close()
