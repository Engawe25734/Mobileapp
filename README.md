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

```bash
pip install fastapi
pip install uvicorn
pip install python-multipart
pip install jinja2
pip install passlib
pip install python-jose
