# RAG Chat Assistant - Frontend

A beautiful, modern web interface for the RAG (Retrieval Augmented Generation) Chat Assistant.

## Features

- 💬 **Interactive Chat Interface**: Clean, modern chat UI with smooth animations
- 📚 **Source Display**: View sources used to generate answers
- 📝 **Conversation History**: View and manage chat history
- 📁 **Document Upload**: Upload documents directly from the browser
- 🎨 **Beautiful Design**: Purple gradient theme with responsive layout
- ⚡ **Real-time**: Instant responses with loading indicators

## Getting Started

### 1. Start the API Server

Run the server using the provided script:

**Windows (PowerShell):**
```powershell
.\start_server.ps1
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

Or manually:
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open the Frontend

Navigate to: `http://localhost:8000`

The frontend will be automatically served by the FastAPI application.

## Usage

### Asking Questions
1. Type your question in the text input at the bottom
2. Press Enter or click the Send button
3. Wait for the AI to generate a response
4. Click on "Sources" to view the documents used

### Uploading Documents
1. Click the "Upload Document" button in the sidebar
2. Select a document file (.pdf, .txt, .md, .csv, .docx)
3. Wait for the upload and processing to complete

### Viewing History
1. Click "View History" to see your conversation history
2. All questions and answers from the current session will be displayed

### Clearing History
1. Click "Clear History" to reset the conversation
2. Confirm the action in the dialog

### Ingesting Data Folder
1. Click "Ingest Data Folder"
2. Enter the path to your data folder
3. All documents in the folder will be processed

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Styling and animations
└── script.js       # Frontend logic and API calls
```

## Browser Support

- Chrome/Edge (Recommended)
- Firefox
- Safari
- Opera

## Customization

### Changing Colors

Edit the CSS variables in `style.css`:

```css
:root {
    --primary-purple: #6366f1;
    --secondary-purple: #8b5cf6;
    /* Add your custom colors */
}
```

### API Configuration

The API URL is configured in `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change this if you're running the API on a different host or port.

## Troubleshooting

### Server is Offline
- Make sure the API server is running
- Check that port 8000 is not blocked
- Verify the API_BASE_URL in script.js matches your server

### Upload Not Working
- Check file size limits
- Ensure the file format is supported
- Verify the data/uploads directory exists

### No Response from AI
- Ensure documents are ingested
- Check the API server logs for errors
- Verify your GROQ_API_KEY is set correctly in .env

## Technologies Used

- **HTML5**: Structure
- **CSS3**: Styling with gradients and animations
- **JavaScript (ES6+)**: Logic and API communication
- **Font Awesome**: Icons
- **FastAPI**: Backend API server

## License

Same as the main RAG project.
