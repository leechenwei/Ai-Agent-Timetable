# Ai-Agent-Timetable
<h3>A smart, AI-powered timetable system for students and teachers, built with React Native, Flask, Firebase, and SambaNova Cloud Api(Meta-Llama). This project helps users efficiently schedule their courses, resolve conflicts, and manage their daily routines with AI assistance.</h3>

<h3>🌐📱 Works for Web / Mobile</h3>

<b><h3>🚀 Features</h3></b>
📆 <b>Automated Timetable Scheduling</b>: AI arranges schedules based on user input.
<br>🧠 <b>AI Chatbot Integration</b>: Users interact with the chatbot to modify and update their timetable.
<br>🔥 <b>Conflict Resolution</b>: AI detects schedule conflicts and suggests replacements.
<br>📂 <b>Firestore Database</b>: Timetables are stored and retrieved dynamically from Firebase.
<br>🔐 <b>User Authentication</b>: Secure login and signup with Firebase Authentication.
<br>🖨 <b>Download Timetable as PDF/CSV/Image</b>: Users can export and save their schedules.
<br><br>
<b><h3>🛠 Tech Stack</h3></b>
<br>Frontend: React Native (Expo, react-native-gifted-chat, react-native-svg)
<br>Backend: Flask (Python)
<br>Database: Firebase Firestore
<br>AI: SambaNova API
<br><br>
<b><h3>💡 Usage</h3></b>
<br>Users log in and input their course schedules.
AI generates an optimized timetable.
Users can modify, delete, or replace events via chatbot.
Timetables are stored per user and per date in Firestore.
Users can download their schedules as PDFs/CSVs or PNG.
<br><br>
<b><h3>🔧 Setup & Installation</h3></b>
<h4>1. Clone the repo:</h4>
<tab>git clone https://github.com/leechenwei/AI-Agent-Timetable.git</tab><br>
<tab>cd AiScheduler</tab>
<br><br>
<h4>2. Install dependencies:</h4>
<tab>npm install  # For React Native</tab><br>
<tab>pip install -r requirements.txt  # For Flask backend</tab>
<br>
<br>
<h5>Run the project:</h5>
Frontend: npx expo start  # Make sure you cd to AiScheduler first <br> 
Backend: python app.py<br>


<br><br>
<h2 style="color: red;">! IMPORTANT INFORMATION</h2>
<h5>1. Create the .env file on /AiScheduler/.env and replace with your own credentials and information</h5>
<h5>2. Retrieve SAMBANOVA CLOUD API key/Model from <a href="https://cloud.sambanova.ai/apis" target="_blank">SambaNova Cloud</a></h5>
<h5>3. Retrieve Firebase .json Credential file from <a href="https://console.firebase.google.com/" target="_blank">Firebase Console</a></h5>
