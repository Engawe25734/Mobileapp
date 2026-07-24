# Mobileapp
# chatMe - Real-Time Mobile Chat Application

## Project Description

chatMe is a real-time messaging application inspired by modern chat platforms. It allows users to create accounts, log in, exchange messages instantly, share files, images, audio, and videos, and communicate through audio/video call features.

---

# Features

## User Authentication
- User registration
- User login
- Secure password authentication
- Token-based session handling

## Real-Time Messaging
- Private one-to-one chat
- WebSocket-based instant communication
- Message history retrieval
- Online/offline user status
- Typing indicators
- Message delivery/read receipts

## File and Media Sharing
Users can send:
- Images
- Videos
- Audio files
- Documents

Supported uploads:
- JPG
- PNG
- GIF
- MP4
- MP3
- WAV
- PDF
- DOC/DOCX
- Other supported file formats

## Calling Features
- Audio call signaling
- Video call signaling
- WebRTC communication support
- Group call rooms

## User Interface
- WhatsApp-inspired interface
- Responsive mobile design
- Dark mode
- Emoji support
- Contact sidebar
- Chat history view

---

# Technology Stack

## Backend
- Python 3.x
- FastAPI
- Uvicorn
- WebSocket
- SQLite Database

## Frontend
- HTML5
- CSS3
- JavaScript
- WebRTC API

## Libraries

Install required packages:

pip install fastapi

pip install uvicorn

pip install python-multipart

pip install jinja2

pip install passlib

pip install python-jose

System Requirements

Hardware Requirements

Minimum:

Dual-core processor
4GB RAM
500MB free storage

Recommended:

Quad-core processor
8GB RAM
1GB free storage
Software Requirements

Operating Systems:

Windows 10/11
Linux
macOS

Required software:

Python 3.10 or newer

Web browser:

Google Chrome
Microsoft Edge
Firefox

Project Structure
Mobileapp/

│
├── server.py

├── websocket_manager.py

├── database.py

├── auth.py

├── models.py

│

├── templates/

│   └── index.html

│

├── static/

│   ├── style.css

│   └── app.js

│

├── uploads/

│

└── chat.db

Running the Application
1. Clone or download project
   
   git clone <repository-url>
   
.Navcigate into the project:

  cd Mobileapp
  
3. Install dependencies
   
   pip install -r requirements.txt
   
5. Start the server
6. 
   uvicorn server:app --host 0.0.0.0 --port 8000
   
   Successful startup:
   
   Application startup complete
   
   Uvicorn running on http://0.0.0.0:8000
   
8. Open Application

Open browser:
http://localhost:8000
Database

The application automatically creates:

chat.db

Database stores:

Users
Conversations
Messages
Attachments

Future Improvements

Push notifications

End-to-end encryption

User profile pictures

Message reactions

Cloud file storage

Mobile Android/iOS deployment



