import React, { useState } from 'react';
import ChatWidget from './components/ChatWidget';
import FileUpload from './components/FileUpload';
import DocumentManager from './components/DocumentManager';
import './App.css';

function App() {
  const [showUpload, setShowUpload] = useState(false);
  const [showDocuments, setShowDocuments] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  const handleUploadComplete = (response: any) => {
    setUploadStatus(`Successfully uploaded: ${response.file_name || 'data'}`);
    setTimeout(() => setUploadStatus(''), 5000);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div style={{ textAlign: 'left' }}>
            <h1 style={{ 
              color: '#e8eaed',
              fontSize: '28px',
              fontWeight: '500',
              letterSpacing: '-0.01em',
              margin: '0 0 4px 0',
              fontFamily: 'Google Sans, -apple-system, BlinkMacSystemFont, sans-serif'
            }}>
              AI Support Assistant
            </h1>
            <p style={{ 
              color: '#9aa0a6', 
              fontSize: '14px', 
              margin: '0',
              fontWeight: '400'
            }}>
              Intelligent support powered by your documents
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button 
              onClick={() => {
                setShowDocuments(!showDocuments);
                if (showUpload) setShowUpload(false);
              }}
              style={{
                padding: '8px 16px',
                background: showDocuments 
                  ? 'rgba(138, 180, 248, 0.2)' 
                  : 'rgba(255, 255, 255, 0.08)',
                color: showDocuments ? '#8ab4f8' : '#e8eaed',
                border: showDocuments ? '1px solid rgba(138, 180, 248, 0.3)' : '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '13px',
                transition: 'all 0.2s cubic-bezier(0.2, 0, 0, 1)',
                backdropFilter: 'blur(8px)',
                fontFamily: 'Google Sans, sans-serif',
                height: '36px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>📚</span>
              <span>{showDocuments ? 'Sources' : 'Sources'}</span>
            </button>
            <button 
              onClick={() => {
                setShowUpload(!showUpload);
                if (showDocuments) setShowDocuments(false);
              }}
              style={{
                padding: '8px 16px',
                background: showUpload 
                  ? 'rgba(251, 188, 4, 0.2)' 
                  : 'rgba(255, 255, 255, 0.08)',
                color: showUpload ? '#fbbc04' : '#e8eaed',
                border: showUpload ? '1px solid rgba(251, 188, 4, 0.3)' : '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '13px',
                transition: 'all 0.2s cubic-bezier(0.2, 0, 0, 1)',
                backdropFilter: 'blur(8px)',
                fontFamily: 'Google Sans, sans-serif',
                height: '36px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>{showUpload ? '✕' : '📤'}</span>
              <span>{showUpload ? 'Close' : 'Upload'}</span>
            </button>
          </div>
        </div>
        
        {uploadStatus && (
          <div style={{
            margin: '16px 0 0 0',
            padding: '12px 16px',
            background: 'rgba(52, 168, 83, 0.15)',
            color: '#81c995',
            borderRadius: '8px',
            border: '1px solid rgba(52, 168, 83, 0.3)',
            backdropFilter: 'blur(8px)',
            fontWeight: '400',
            fontSize: '13px',
            textAlign: 'left',
            fontFamily: 'Google Sans, sans-serif'
          }}>
            <span style={{ marginRight: '8px' }}>✓</span>
            {uploadStatus}
          </div>
        )}
      </header>
      
      <main className="App-main">
        <div style={{ 
          display: 'flex', 
          gap: '24px', 
          alignItems: 'flex-start', 
          flexWrap: 'wrap',
          justifyContent: 'center',
          padding: '0',
          maxWidth: '1200px',
          margin: '0 auto',
          width: '100%'
        }}>
          {showDocuments && (
            <DocumentManager 
              selectedDocuments={selectedDocuments}
              onDocumentSelectionChange={setSelectedDocuments}
            />
          )}
          
          {showUpload && (
            <FileUpload onUploadComplete={handleUploadComplete} />
          )}
          
          <div style={{ 
            flex: (showUpload || showDocuments) ? 'none' : '1', 
            display: 'flex',
            justifyContent: 'center'
          }}>
            <ChatWidget
              title="💬 AI Assistant"
              welcomeMessage="Hello! I'm here to help you with your questions. Upload documents or ask me anything!"
              placeholder="Ask me anything..."
              selectedDocuments={selectedDocuments}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
