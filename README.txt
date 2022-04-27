Assignment 2 Usage

Please be sure the following files are in the same directory before running:
    Sender.py
    Receiver.py
    timer.py
    packet.py
    udt.py
    bio.txt

1. First, run Receiver.py with either the Stop-n-wait protocol or with the Go-back-N protocol.
    a. Ex: python3 Receiver.py <-snw|-gbn> <file_name_to_write.txt>
2. Second, run Sender.py with the same protocol used for the Receiver
    b. Ex: python3 Sender.py <-snw|gbn> <file_name_to_read.txt>
3. The file selected in the Sender will be sent over the selected protocol to the receiver,
   who will then write to the specified file.
