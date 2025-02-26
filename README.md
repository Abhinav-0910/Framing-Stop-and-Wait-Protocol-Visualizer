An interactive Streamlit-based tool for visualizing framing techniques (Byte Count, Byte Stuffing, Bit Stuffing) and implementing the Stop-and-Wait ARQ protocol for reliable data transmission.

Features
✅ Supports Byte Count, Flag Byte Stuffing, and Bit Stuffing framing methods
✅ Implements Stop-and-Wait ARQ for error detection & retransmission
✅ Real-time client-server communication using socket programming
✅ Interactive visualizations with Plotly for framing techniques
✅ Logs sender, receiver, and acknowledgment (ACK) messages


Project Structure
📂 framing-visualizer
 ┣ 📜 main.py        # Streamlit-based UI & visualization
 ┣ 📜 s2.py          # Server implementation (Stop-and-Wait Protocol)
 ┣ 📜 requirements.txt  # Required Python dependencies
 ┗ 📜 README.md       # Project documentation
