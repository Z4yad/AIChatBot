import React, { useState } from 'react';
import styled from 'styled-components';

const UploadContainer = styled.div`
  background: rgba(32, 33, 36, 0.95);
  backdrop-filter: blur(40px) saturate(1.8);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.08);
  max-width: 420px;
  width: 420px;
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const Title = styled.h2`
  color: #e8eaed;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 500;
  text-align: center;
`;

const TabContainer = styled.div`
  display: flex;
  background: rgba(60, 64, 67, 0.6);
  border-radius: 8px;
  padding: 2px;
  margin-bottom: 20px;
`;

const Tab = styled.button<{ active: boolean }>`
  flex: 1;
  padding: 8px 16px;
  border: none;
  background: ${props => props.active ? '#8ab4f8' : 'transparent'};
  color: ${props => props.active ? '#202124' : '#9aa0a6'};
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-size: 13px;
  font-family: 'Google Sans', sans-serif;

  &:hover {
    background: ${props => props.active ? '#aecbfa' : 'rgba(255, 255, 255, 0.08)'};
  }
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #e8eaed;
  font-size: 14px;
  font-family: 'Google Sans', sans-serif;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(60, 64, 67, 0.8);
  color: #e8eaed;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-family: 'Google Sans', sans-serif;

  &:focus {
    outline: none;
    border-color: #8ab4f8;
    box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.2);
    background: rgba(60, 64, 67, 1);
  }
  
  &::placeholder {
    color: #9aa0a6;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(60, 64, 67, 0.8);
  color: #e8eaed;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-family: 'Google Sans', sans-serif;

  &:focus {
    outline: none;
    border-color: #8ab4f8;
    box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.2);
    background: rgba(60, 64, 67, 1);
  }
`;

const FileDropArea = styled.div<{ isDragOver: boolean }>`
  border: 2px dashed ${props => props.isDragOver ? '#8ab4f8' : 'rgba(255, 255, 255, 0.12)'};
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  background: ${props => props.isDragOver ? 'rgba(0, 122, 255, 0.05)' : 'rgba(248, 248, 248, 0.5)'};
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 24px;

  &:hover {
    border-color: #007AFF;
    background: rgba(0, 122, 255, 0.05);
    transform: translateY(-2px);
  }
`;

const UploadButton = styled.button`
  background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 122, 255, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: #86868b;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const StatusMessage = styled.div<{ type: 'success' | 'error' | 'info' }>`
  padding: 16px;
  border-radius: 12px;
  margin-top: 20px;
  font-weight: 500;
  background: ${props => {
    switch (props.type) {
      case 'success': return 'rgba(52, 199, 89, 0.1)';
      case 'error': return 'rgba(255, 59, 48, 0.1)';
      case 'info': return 'rgba(0, 122, 255, 0.1)';
      default: return 'rgba(248, 248, 248, 0.8)';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'success': return '#34C759';
      case 'error': return '#FF3B30';
      case 'info': return '#007AFF';
      default: return '#1d1d1f';
    }
  }};
  border: 1px solid ${props => {
    switch (props.type) {
      case 'success': return 'rgba(52, 199, 89, 0.2)';
      case 'error': return 'rgba(255, 59, 48, 0.2)';
      case 'info': return 'rgba(0, 122, 255, 0.2)';
      default: return 'rgba(0, 0, 0, 0.1)';
    }
  }};
`;

const ProgressBar = styled.div<{ progress: number }>`
  width: 100%;
  height: 6px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
  margin-top: 16px;
  overflow: hidden;

  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${props => props.progress}%;
    background: linear-gradient(90deg, #007AFF, #0056CC);
    transition: width 0.3s ease;
    border-radius: 3px;
  }
`;

interface FileUploadProps {
  onUploadComplete?: (response: any) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [activeTab, setActiveTab] = useState<'file' | 'json'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState<{type: 'success' | 'error' | 'info', text: string} | null>(null);
  
  // Form fields
  const [title, setTitle] = useState('');
  const [productVersion, setProductVersion] = useState('');
  const [tags, setTags] = useState('');
  const [dataType, setDataType] = useState('helpdesk');

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const validateFile = (file: File): string | null => {
    if (activeTab === 'file') {
      const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedTypes.includes(fileExtension)) {
        return `File type not supported. Allowed: ${allowedTypes.join(', ')}`;
      }
    } else if (activeTab === 'json') {
      if (!file.name.toLowerCase().endsWith('.json')) {
        return 'Please select a JSON file';
      }
    }
    
    if (file.size > 200 * 1024 * 1024) { // 200MB limit
      return 'File size must be less than 200MB';
    }
    
    return null;
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setStatusMessage({ type: 'error', text: 'Please select a file' });
      return;
    }

    const validationError = validateFile(selectedFile);
    if (validationError) {
      setStatusMessage({ type: 'error', text: validationError });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setStatusMessage({ type: 'info', text: 'Uploading file...' });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      if (activeTab === 'file') {
        if (title) formData.append('title', title);
        if (productVersion) formData.append('product_version', productVersion);
        if (tags) formData.append('tags', tags);
      } else {
        formData.append('data_type', dataType);
        if (productVersion) formData.append('product_version', productVersion);
      }

      const endpoint = activeTab === 'file' ? '/upload/file' : '/upload/json';
      const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      
      // Use XMLHttpRequest for upload progress and better large-file handling
      const xhr = new XMLHttpRequest();
      await new Promise<void>((resolve, reject) => {
        xhr.open('POST', `${apiUrl}${endpoint}`);
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const pct = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(pct);
          }
        };
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve();
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.detail || 'Upload failed'));
            } catch (e) {
              reject(new Error('Upload failed'));
            }
          }
        };
        xhr.onerror = () => reject(new Error('Network error'));
        xhr.send(formData);
      });

      const result = JSON.parse(xhr.responseText);
      setUploadProgress(100);
      setStatusMessage({ 
        type: 'success', 
        text: `Upload successful! ${result.message}` 
      });
      
      // Reset form
      setSelectedFile(null);
      setTitle('');
      setProductVersion('');
      setTags('');
      
      if (onUploadComplete) {
        onUploadComplete(result);
      }

    } catch (error) {
      setStatusMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Upload failed' 
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <UploadContainer>
      <Title>Upload Knowledge Base Content</Title>
      
      <TabContainer>
        <Tab 
          active={activeTab === 'file'} 
          onClick={() => setActiveTab('file')}
        >
          📄 Documents
        </Tab>
        <Tab 
          active={activeTab === 'json'} 
          onClick={() => setActiveTab('json')}
        >
          📊 JSON Data
        </Tab>
      </TabContainer>

      <FileDropArea
        isDragOver={isDragOver}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept={activeTab === 'file' ? '.pdf,.docx,.txt,.md' : '.json'}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        {selectedFile ? (
          <div>
            <p><strong>Selected:</strong> {selectedFile.name}</p>
            <p>Size: {(selectedFile.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div>
            <p>📁 Drag & drop your file here, or click to browse</p>
            <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px' }}>
              {activeTab === 'file' 
                ? 'Supported: PDF, DOCX, TXT, MD (max 10MB)'
                : 'Supported: JSON files (max 10MB)'}
            </p>
          </div>
        )}
      </FileDropArea>

      {activeTab === 'file' && (
        <>
          <FormGroup>
            <Label>Title (optional)</Label>
            <Input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Document title"
            />
          </FormGroup>

          <FormGroup>
            <Label>Product Version (optional)</Label>
            <Input
              type="text"
              value={productVersion}
              onChange={(e) => setProductVersion(e.target.value)}
              placeholder="e.g., v2.1.0"
            />
          </FormGroup>

          <FormGroup>
            <Label>Tags (optional)</Label>
            <Input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="Comma-separated tags: api, authentication, troubleshooting"
            />
          </FormGroup>
        </>
      )}

      {activeTab === 'json' && (
        <>
          <FormGroup>
            <Label>Data Type</Label>
            <Select
              value={dataType}
              onChange={(e) => setDataType(e.target.value)}
            >
              <option value="helpdesk">Helpdesk Tickets</option>
              <option value="zendesk">Zendesk Tickets</option>
              <option value="custom">Custom Data</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Product Version (optional)</Label>
            <Input
              type="text"
              value={productVersion}
              onChange={(e) => setProductVersion(e.target.value)}
              placeholder="e.g., v2.1.0"
            />
          </FormGroup>
        </>
      )}

      <UploadButton
        onClick={uploadFile}
        disabled={!selectedFile || isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload & Process'}
      </UploadButton>

      {isUploading && (
        <ProgressBar progress={uploadProgress} />
      )}

      {statusMessage && (
        <StatusMessage type={statusMessage.type}>
          {statusMessage.text}
        </StatusMessage>
      )}
    </UploadContainer>
  );
};

export default FileUpload;
