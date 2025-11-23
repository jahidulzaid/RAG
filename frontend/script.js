// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let sessionId = null;
let isProcessing = false;

// DOM Elements
const messagesContainer = document.getElementById('messages');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const viewHistoryBtn = document.getElementById('view-history-btn');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const ingestFolderBtn = document.getElementById('ingest-folder-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const historyModal = document.getElementById('history-modal');
const closeHistoryBtn = document.getElementById('close-history-btn');
const historyContent = document.getElementById('history-content');
const statusText = document.getElementById('status-text');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkServerStatus();
    setupEventListeners();
    autoResizeTextarea();
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    viewHistoryBtn.addEventListener('click', showHistory);
    clearHistoryBtn.addEventListener('click', clearHistory);
    ingestFolderBtn.addEventListener('click', ingestDataFolder);
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    closeHistoryBtn.addEventListener('click', () => historyModal.classList.remove('show'));
    
    // Close modal on background click
    historyModal.addEventListener('click', (e) => {
        if (e.target === historyModal) {
            historyModal.classList.remove('show');
        }
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    questionInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        const data = await response.json();
        
        if (data.status === 'online') {
            statusText.textContent = 'Ready';
            statusText.style.color = 'var(--white)';
        }
    } catch (error) {
        statusText.textContent = 'Offline';
        statusText.style.color = '#fbbf24';
        showToast('Server is offline. Please start the server.', 'error');
    }
}

// Send message
async function handleSendMessage() {
    const question = questionInput.value.trim();
    
    if (!question || isProcessing) return;
    
    // Clear welcome message
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    // Add user message
    addMessage(question, 'user');
    
    // Clear input
    questionInput.value = '';
    questionInput.style.height = 'auto';
    
    // Show loading
    const loadingId = showLoading();
    isProcessing = true;
    sendBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                session_id: sessionId,
                maintain_history: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Store session ID
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
        // Remove loading
        removeLoading(loadingId);
        
        // Add AI response
        addMessage(data.answer, 'ai', data.sources);
        
    } catch (error) {
        removeLoading(loadingId);
        showToast('Error: ' + error.message, 'error');
        addMessage('Sorry, I encountered an error. Please try again.', 'ai');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// Add message to chat
function addMessage(text, sender, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    contentDiv.appendChild(bubble);
    
    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesToggle = document.createElement('button');
        sourcesToggle.className = 'sources-toggle';
        sourcesToggle.innerHTML = `<i class="fas fa-book"></i> Sources (${sources.length})`;
        
        const sourcesContent = document.createElement('div');
        sourcesContent.className = 'sources-content';
        
        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            
            const filename = source.metadata?.source || 'Unknown Source';
            const content = source.content.substring(0, 150) + '...';
            
            sourceItem.innerHTML = `
                <div class="source-filename">${index + 1}. ${filename}</div>
                <div class="source-text">${content}</div>
            `;
            
            sourcesContent.appendChild(sourceItem);
        });
        
        sourcesToggle.addEventListener('click', () => {
            sourcesContent.classList.toggle('show');
            const icon = sourcesToggle.querySelector('i');
            icon.className = sourcesContent.classList.contains('show') 
                ? 'fas fa-chevron-up' 
                : 'fas fa-book';
        });
        
        contentDiv.appendChild(sourcesToggle);
        contentDiv.appendChild(sourcesContent);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show loading indicator
function showLoading() {
    const loadingId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.id = loadingId;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
        <span>Thinking...</span>
    `;
    
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return loadingId;
}

// Remove loading indicator
function removeLoading(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Show conversation history
async function showHistory() {
    if (!sessionId) {
        showToast('No conversation history yet.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }
        
        const data = await response.json();
        
        if (data.history.length === 0) {
            historyContent.innerHTML = '<p style="text-align: center; color: var(--text-light);">No conversation history yet.</p>';
        } else {
            historyContent.innerHTML = data.history.map((item, index) => `
                <div class="history-item">
                    <div class="history-question">
                        <i class="fas fa-user"></i>
                        <strong>Q${index + 1}:</strong> ${item.question}
                    </div>
                    <div class="history-answer">
                        <strong><i class="fas fa-robot"></i> A:</strong> ${item.answer}
                    </div>
                </div>
            `).join('');
        }
        
        historyModal.classList.add('show');
        
    } catch (error) {
        showToast('Error loading history: ' + error.message, 'error');
    }
}

// Clear conversation history
async function clearHistory() {
    if (!sessionId) {
        showToast('No conversation history to clear.', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to clear the conversation history?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear history');
        }
        
        showToast('History cleared successfully!', 'success');
        
        // Clear messages from UI
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-robot welcome-icon"></i>
                <h2>Welcome to RAG Chat Assistant</h2>
                <p>Ask me anything about your documents!</p>
            </div>
        `;
        
    } catch (error) {
        showToast('Error clearing history: ' + error.message, 'error');
    }
}

// Ingest data folder
async function ingestDataFolder() {
    const folderPath = prompt('Enter the path to the data folder:', './data');
    
    if (!folderPath) return;
    
    showToast('Ingesting documents...', 'success');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/ingest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                path: folderPath
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to ingest documents');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Successfully ingested ${data.documents_processed} document chunks!`, 'success');
        } else {
            showToast(data.message, 'error');
        }
        
    } catch (error) {
        showToast('Error ingesting documents: ' + error.message, 'error');
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    showToast(`Uploading ${file.name}...`, 'success');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to upload file');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Successfully uploaded and processed ${file.name}!`, 'success');
        } else {
            showToast(data.message, 'error');
        }
        
    } catch (error) {
        showToast('Error uploading file: ' + error.message, 'error');
    } finally {
        // Reset file input
        fileInput.value = '';
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
