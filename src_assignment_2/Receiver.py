# Networks Assignment 2
# Erik Macik
#

# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)

# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock, filename):
    file = open(filename, "w")
    ack_num = 0
    endStr = ''

    # Continually receive packets until we get the last one
    while endStr != 'END':
        pkt, senderaddr = udt.recv(sock)
        seq, data = packet.extract(pkt)

        if seq == ack_num:
            ack_packet = packet.make(ack_num, ''.encode())
            print("sending ack for packet#", ack_num)
            udt.send(ack_packet, sock, SENDER_ADDR)
            ack_num += 1
            # Write the data to a file if it's not the end
            endStr = data.decode()
            if endStr != 'END':
                file.write(endStr)
        # else:
        #     if ack_num-1 < 0:
        #         continue
        #     ack_packet = packet.make(ack_num-1, ''.encode())
        #     print('bad packet, replying with the one I want#', ack_num - 1)
        #     udt.send(ack_packet, sock, SENDER_ADDR)
        

        # # If we already have this packet, reply with the number we are expecting
        # if seq != expecting_num:
        #     ack_packet = packet.make(expecting_num-1, ''.encode())
        #     print("Sending Repeat ack#", expecting_num-1)
        #     udt.send(ack_packet, sock, SENDER_ADDR)
        #     continue

        # # Write the data to a file if it's not the end
        # endStr = data.decode()
        # if endStr != 'END':
        #     file.write(endStr)

        # # Send ack of this packet to sender
        # print("Received #", seq, "\n")
        # ack_packet = packet.make(expecting_num, ''.encode())
        # print("Sending ack#", expecting_num)
        # udt.send(ack_packet, sock, SENDER_ADDR)
        
        # # Keep track of sequence numbers received
        # expecting_num += 1



# Receive packets from the sender w/ SR protocol
def receive_sr(sock, filename):
    ### COPIED FROM receive_snw() ###
    # File to write to
    return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock, filename):
    # File to write to
    file = open(filename, "w")
    ack_number = 0
    endStr = ''

    # Continually receive packets until we get the last one
    while endStr != 'END':
        pkt, senderaddr = udt.recv(sock)
        seq, data = packet.extract(pkt)

        # If we already have this packet, just send back a repeat ack
        if seq < ack_number:
            ack_packet = packet.make(seq, ''.encode())
            print("Sending Repeat ack#", seq)
            udt.send(ack_packet, sock, SENDER_ADDR)
            continue

        # Write the data to a file if it's not the end
        endStr = data.decode()
        if endStr != 'END':
            file.write(endStr)

        # Send ack of this packet to sender
        print("Received #", seq, "\n")
        ack_packet = packet.make(ack_number, ''.encode())
        print("Sending ack#", ack_number)
        udt.send(ack_packet, sock, SENDER_ADDR)
        
        # Keep track of sequence numbers received
        ack_number += 1


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Expected protocol and filename as command line argument')
        print('Usage: <-snw|-gbn> <filename>')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)

    # get protocol and filename
    protocol = sys.argv[1]
    filename = sys.argv[2]
    
    if protocol == '-snw':
        # Receive with stop n wait protocol
        print('Using stop n wait')
        receive_snw(sock, filename)
    elif protocol == '-gbn':
        # Receive with go back n protocol
        print('uisng go back n')
        receive_gbn(sock, filename)
    else:
        print('Bad protocol, use one of these: <-snw|-gbn>')

    # Close the socket
    sock.close()