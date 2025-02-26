import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px
import socket


# Server configuration
SERVER_ADDRESS = "localhost"  # Change to your server's address if needed
SERVER_PORT = 65432  # Port number to connect to the server
TIMEOUT_MS = 5000  # Timeout in milliseconds for retransmission

# Function for Byte Count Framing
def byte_count_framing(data_list):
    framed_data = ''
    for data in data_list:
        length = len(data) + 1  # +1 for the length digit itself
        framed_data += str(length) + data + " "  # Added space for clarity
    return framed_data.strip()  # Ensure no trailing space

# Function for Flag Bytes with Byte Stuffing
def flag_bytes_with_byte_stuffing(input_data, flag, escape):
    stuffed_data = ''
    for char in input_data:
        if char == flag or char == escape:
            stuffed_data += escape + char
        else:
            stuffed_data += char
    
    return flag + " " + stuffed_data + " " + flag

# Function for Flag Bits with Bit Stuffing
def flag_bits_with_bit_stuffing(data):
    flag = '01111110'
    stuffed_bits = ''
    count = 0
    for bit in data:
        if bit == '1':
            count += 1
            stuffed_bits += '1'
            if count == 5:
                stuffed_bits += '0'
                count = 0
        else:
            stuffed_bits += '0'
            count = 0
    return flag + " " + stuffed_bits + " " + flag

def send_frame_with_timeout(seq_num, frame, client_socket, log_list):
    ack_received = False
    
    while not ack_received:
        client_socket.sendall(f"{frame}\n".encode())
        log_list.append(f"Sent frame: {frame}")  # Log the sent frame

        # Set a timeout for receiving the ACK
        client_socket.settimeout(TIMEOUT_MS / 1000)

        try:
            response = client_socket.recv(1024).decode().strip()
            if response and response.startswith(f"ACK:{seq_num}"):
                log_list.append(f"Received ACK for seqNum: {seq_num}")  # Log the received ACK
                ack_received = True
            else:
                log_list.append("Received wrong ACK or no ACK. Retransmitting...")  # Log wrong ACK
        except socket.timeout:
            log_list.append("ACK not received in time. Retransmitting frame...")  # Log timeout

def handle_connection(data_string):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_ADDRESS, SERVER_PORT))        
        seq_num = 0
        words = data_string.split()
        
        # Create a log list to capture send/receive logs
        transmission_logs = []
        
        # Create placeholders for logs
        sender_logs = []
        receiver_logs = []
        ack_logs = []  # New log for ACKs
        sender_placeholder = st.empty()
        receiver_placeholder = st.empty()
        ack_placeholder = st.empty()  # New placeholder for ACKs
        transmission_placeholder = st.empty()  # New placeholder for transmission logs

        
        for word in words:
            frame = f"{seq_num}:{word}"
            send_frame_with_timeout(seq_num, frame, client_socket, transmission_logs)  # Send the frame
            receiver_logs.append(f"Frame {frame} sent.")
            ack_logs.append(f"ACK for seqNum: {seq_num}")  # Log the ACK
            sender_logs.append(f"Sending frame: {frame}")

            seq_num += 1
            time.sleep(0.1)  # Small delay between sends to avoid overwhelming the server

        # Display transmission logs in the app
        transmission_placeholder.table(pd.DataFrame(transmission_logs, columns=["Transmission Logs"]))
        sender_placeholder.table(pd.DataFrame(sender_logs, columns=["Sender Logs"]))  # Update sender logs display
        receiver_placeholder.table(pd.DataFrame(receiver_logs, columns=["Receiver Logs"]))  # Update receiver logs display
        ack_placeholder.table(pd.DataFrame(ack_logs, columns=["ACK Logs"]))  # Update ACK logs display

        print("All data sent. Closing connection...")
        client_socket.sendall("exit\n".encode())  # Send exit message to server
        seq_num=0

# Streamlit App Layout
st.set_page_config(layout="wide")
st.title("🖼️ Framing Algorithms Interactive Visualization")

# Add a custom CSS to improve the overall look
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stSelectbox {
        background-color: #000000;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
    }
    .stTextArea textarea {
        background-color: #333333;
        color: white;
    }
    .css-145kmo2 {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([1, 2])

# Initialize session state for navigation
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if not st.session_state.show_results:
    with col1:
        st.subheader("Input Parameters")
        # User selects framing method
        method = st.selectbox("Choose a Framing Method", 
                            ["Byte Count", 
                            "Flag Bytes with Byte Stuffing", 
                            "Flag Bits with Bit Stuffing"])

        # Input field changes based on the selected method
        if method == "Byte Count":
            input_data = st.text_area("Enter your frames of data (space b/w frames):", "25642 15632 6541")
        elif method == "Flag Bytes with Byte Stuffing":
            input_data = st.text_input("Enter your message:", "Hello F World E How F are you")
            st.info("Note: Flag is denoted as 'F' and escape character is 'E'.")
        elif method == "Flag Bits with Bit Stuffing":
            input_data = st.text_area("Enter your data in bits (e.g., 1010110):", "1010110")
            st.info("Note: The flag used for bit stuffing is 01111110")

        submit_button = st.button("Submit")

    # Handle submission and navigate to results page
    with col2:
        st.subheader("Results")
        if submit_button:
            result = None
            if method == "Byte Count":
                data_list = input_data.split()
                result = byte_count_framing(data_list)
                st.write("**Input Frames:**")
                st.code(input_data)
                st.write("**Framed Message:**")
                st.code(result)
                input_len = len(input_data.replace(" ", ""))
                framed_len = len(result.replace(" ", ""))
            
            elif method == "Flag Bytes with Byte Stuffing":
                result = flag_bytes_with_byte_stuffing(input_data, "F", "E")  # Pass user-defined characters
                st.write("**Input Message:**")
                st.code(input_data)
                st.write("**Framed Message:**")
                st.code(result)
                input_len = len(input_data.replace(" ", ""))
                framed_len = len(result.replace(" ", ""))
            
            elif method == "Flag Bits with Bit Stuffing":
                if not set(input_data).issubset({'0', '1'}):
                    st.error("Please enter valid binary data (only 0s and 1s).")
                    st.stop()
                    
                result = flag_bits_with_bit_stuffing(input_data)
                st.write("**Input Message:**")
                st.code(input_data)
                st.write("**Framed Message:**")
                st.code(result)
                input_len = len(input_data.replace(" ", ""))
                framed_len = len(result.replace(" ", ""))

            st.write(f"**Input Length:** {input_len}")
            st.write(f"**Framed Length:** {framed_len}")

            # Visualizations
            st.write("### Length Comparison")
            fig = px.bar(
                x=[input_len, framed_len],
                y=['Input', 'Framed'],
                orientation='h',
                labels={'x': 'Length', 'y': 'Data Type'},
                color=['Input', 'Framed'],
                color_discrete_map={'Input': 'royalblue', 'Framed': 'lightgreen'},
                title="Input vs Framed Data Length"
            )
            fig.update_layout(height=300, width=600)
            st.plotly_chart(fig)

            # Add a visual representation of the framing process
            st.write("### Framing Process Visualization")
            if method == "Byte Count":
                fig = go.Figure()
                for i, frame in enumerate(data_list):
                    fig.add_shape(type="rect", x0=i*2, y0=0, x1=i*2+1.8, 
                                fillcolor="lightblue", line=dict(color="royalblue"))
                    fig.add_annotation(x=i*2+0.9, y=0.5, text=f"<b>{frame}</b>", showarrow=False, font=dict(color="black", size=14), align="center")
                fig.update_layout(
                    height=200, 
                    width=800,  # Increased width
                    showlegend=False, 
                    xaxis=dict(showticklabels=False, range=[-0.5, len(data_list)*2]), 
                    yaxis=dict(showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig)

            elif method in ["Flag Bytes with Byte Stuffing", "Flag Bits with Bit Stuffing"]:
                parts = result.split()
                fig = go.Figure()
                for i, part in enumerate(parts):
                    color = "lightgreen" if i in [0, len(parts)-1] else "lightblue"
                    fig.add_shape(type="rect", x0=i*2, y0=0, x1=i*2+1.8, 
                                fillcolor=color, line=dict(color="royalblue"))
                    fig.add_annotation(x=i*2+0.9, y=0.5, text=f"<b>{part}</b>", showarrow=False, font=dict(color="black"))
                fig.update_layout(
                    height=200, 
                    width=1000,  # Increased width
                    showlegend=False, 
                    xaxis=dict(showticklabels=False, range=[-0.5, len(parts)*2]), 
                    yaxis=dict(showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig)
                
            # Add a horizontal line
            st.markdown("---")  # This creates a horizontal line

            # Add title for Stop-and-Wait Protocol
            st.markdown("<h2 style='text-align: center;'>Implementing Stop-and-Wait Protocol</h2>", unsafe_allow_html=True)             
            # Store results in session state
            st.session_state.result = result
            handle_connection(result)  # Send the framed message and log the process                
            # Update session state with logs
            st.session_state.sender_logs = []  # Store sender logs
            st.session_state.receiver_logs = []  # Store receiver logs