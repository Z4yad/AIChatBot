import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const DocumentsContainer = styled.div`
  background: rgba(32, 33, 36, 0.95);
  backdrop-filter: blur(40px) saturate(1.8);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.08);
  max-width: 380px;
  width: 380px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const Title = styled.h3`
  color: #e8eaed;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const RefreshButton = styled.button`
  background: rgba(138, 180, 248, 0.2);
  border: 1px solid rgba(138, 180, 248, 0.3);
  border-radius: 16px;
  padding: 6px 12px;
  color: #8ab4f8;
  font-weight: 500;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-family: 'Google Sans', sans-serif;

  &:hover {
    background: rgba(138, 180, 248, 0.3);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const DocumentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
`;

const DocumentCard = styled.div<{ selected: boolean }>`
  background: ${props => props.selected ? 'rgba(138, 180, 248, 0.15)' : 'rgba(60, 64, 67, 0.6)'};
  border: 1px solid ${props => props.selected ? '#8ab4f8' : 'rgba(255, 255, 255, 0.08)'};
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  position: relative;
  backdrop-filter: blur(8px);

  &:hover {
    background: ${props => props.selected ? 'rgba(138, 180, 248, 0.2)' : 'rgba(60, 64, 67, 0.8)'};
    transform: translateY(-1px);
    border-color: ${props => props.selected ? '#8ab4f8' : 'rgba(255, 255, 255, 0.12)'};
  }
`;

const DocumentInfo = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
`;

const DocumentDetails = styled.div`
  flex: 1;
`;

const DocumentTitle = styled.div`
  font-weight: 500;
  color: #e8eaed;
  font-size: 14px;
  margin-bottom: 4px;
  line-height: 1.4;
  font-family: 'Google Sans', sans-serif;
`;

const DocumentMeta = styled.div`
  color: #9aa0a6;
  font-size: 12px;
  margin-bottom: 8px;
  font-family: 'Google Sans', sans-serif;
`;

const DocumentType = styled.span`
  background: rgba(138, 180, 248, 0.2);
  color: #8ab4f8;
  border: 1px solid rgba(138, 180, 248, 0.3);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  font-family: 'Google Sans', sans-serif;
`;

const DeleteButton = styled.button`
  background: rgba(234, 67, 53, 0.2);
  border: 1px solid rgba(234, 67, 53, 0.3);
  border-radius: 16px;
  width: 28px;
  height: 28px;
  color: #ea4335;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-size: 14px;
  font-weight: 500;

  &:hover {
    background: rgba(234, 67, 53, 0.3);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #9aa0a6;
  font-family: 'Google Sans', sans-serif;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const FilterHeader = styled.div`
  margin-top: 24px;
  margin-bottom: 16px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
`;

const FilterTitle = styled.h4`
  color: #e8eaed;
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 12px 0;
  font-family: 'Google Sans', sans-serif;
`;

const SelectAllButton = styled.button`
  background: rgba(138, 180, 248, 0.2);
  border: 1px solid rgba(138, 180, 248, 0.3);
  color: #8ab4f8;
  border-radius: 16px;
  padding: 6px 12px;
  font-weight: 500;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  margin-bottom: 16px;
  font-family: 'Google Sans', sans-serif;

  &:hover {
    background: rgba(138, 180, 248, 0.3);
    transform: translateY(-1px);
  }
`;

interface Document {
  id: string;
  title: string;
  source_type: string;
  created_at: string;
  chunks_count: number;
}

interface GroupedDocument {
  id: string; // We'll use the first chunk's ID as the representative
  title: string;
  source_type: string;
  created_at: string;
  chunks_count: number;
  chunk_ids: string[]; // Store all chunk IDs for this document
}

interface DocumentManagerProps {
  selectedDocuments: string[];
  onDocumentSelectionChange: (selected: string[]) => void;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({
  selectedDocuments,
  onDocumentSelectionChange
}) => {
  const [documents, setDocuments] = useState<GroupedDocument[]>([]);
  const [loading, setLoading] = useState(true);

  const groupDocuments = (docs: Document[]): GroupedDocument[] => {
    const grouped = docs.reduce((acc, doc) => {
      const key = `${doc.title}_${doc.source_type}`;
      
      if (!acc[key]) {
        acc[key] = {
          id: doc.id, // Use first chunk's ID as representative
          title: doc.title,
          source_type: doc.source_type,
          created_at: doc.created_at,
          chunks_count: 0,
          chunk_ids: []
        };
      }
      
      acc[key].chunks_count += doc.chunks_count;
      acc[key].chunk_ids.push(doc.id);
      
      // Use the earliest creation date
      if (new Date(doc.created_at) < new Date(acc[key].created_at)) {
        acc[key].created_at = doc.created_at;
      }
      
      return acc;
    }, {} as Record<string, GroupedDocument>);
    
    return Object.values(grouped);
  };

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/documents`);
      if (response.ok) {
        const data = await response.json();
        const rawDocuments = data.documents || [];
        const groupedDocuments = groupDocuments(rawDocuments);
        setDocuments(groupedDocuments);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (document: GroupedDocument) => {
    try {
      const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      
      // Delete all chunks for this document
      await Promise.all(
        document.chunk_ids.map(chunkId => 
          fetch(`${apiUrl}/documents/${chunkId}`, { method: 'DELETE' })
        )
      );
      
      setDocuments(prev => prev.filter(doc => doc.id !== document.id));
      
      // Remove all chunk IDs from selection
      const updatedSelection = selectedDocuments.filter(
        id => !document.chunk_ids.includes(id)
      );
      onDocumentSelectionChange(updatedSelection);
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const toggleDocumentSelection = (document: GroupedDocument) => {
    // Check if any chunk of this document is selected
    const isSelected = document.chunk_ids.some(id => selectedDocuments.includes(id));
    
    if (isSelected) {
      // Remove all chunks of this document from selection
      const newSelection = selectedDocuments.filter(
        id => !document.chunk_ids.includes(id)
      );
      onDocumentSelectionChange(newSelection);
    } else {
      // Add all chunks of this document to selection
      const newSelection = [...selectedDocuments, ...document.chunk_ids];
      onDocumentSelectionChange(newSelection);
    }
  };

  const selectAllDocuments = () => {
    const allChunkIds = documents.flatMap(doc => doc.chunk_ids);
    if (selectedDocuments.length === allChunkIds.length) {
      onDocumentSelectionChange([]);
    } else {
      onDocumentSelectionChange(allChunkIds);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTypeIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'pdf': return '📄';
      case 'docx': return '📝';
      case 'txt': return '📃';
      case 'md': return '📋';
      default: return '📁';
    }
  };

  return (
    <DocumentsContainer>
      <Header>
        <Title>Knowledge Base</Title>
        <RefreshButton onClick={fetchDocuments}>
          🔄 Refresh
        </RefreshButton>
      </Header>

      {documents.length > 0 && (
        <>
          <SelectAllButton onClick={selectAllDocuments}>
            {selectedDocuments.length === documents.length ? 'Deselect All' : 'Select All'}
          </SelectAllButton>

          <FilterHeader>
            <FilterTitle>Source Filter</FilterTitle>
            <div style={{ fontSize: '12px', color: '#9aa0a6', marginBottom: '16px', fontFamily: 'Google Sans, sans-serif' }}>
              {selectedDocuments.length === 0 
                ? 'All sources will be used' 
                : `${selectedDocuments.length} source${selectedDocuments.length > 1 ? 's' : ''} selected`}
            </div>
          </FilterHeader>
        </>
      )}

      <DocumentList>
        {loading ? (
          <EmptyState>
            <EmptyIcon>⏳</EmptyIcon>
            <div>Loading documents...</div>
          </EmptyState>
        ) : documents.length === 0 ? (
          <EmptyState>
            <EmptyIcon>📂</EmptyIcon>
            <div>No documents uploaded yet</div>
            <div style={{ fontSize: '13px', marginTop: '8px' }}>
              Upload some files to get started
            </div>
          </EmptyState>
        ) : (
          documents.map(doc => {
            // Check if any chunk of this document is selected
            const isSelected = doc.chunk_ids.some(id => selectedDocuments.includes(id));
            
            return (
              <DocumentCard 
                key={doc.id}
                selected={isSelected}
                onClick={() => toggleDocumentSelection(doc)}
              >
                <DocumentInfo>
                  <DocumentDetails>
                    <DocumentTitle>
                      {getTypeIcon(doc.source_type)} {doc.title}
                    </DocumentTitle>
                    <DocumentMeta>
                      {formatDate(doc.created_at)} • {doc.chunks_count} chunks
                    </DocumentMeta>
                    <DocumentType>{doc.source_type}</DocumentType>
                  </DocumentDetails>
                  <DeleteButton 
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteDocument(doc);
                    }}
                  >
                    ×
                  </DeleteButton>
                </DocumentInfo>
              </DocumentCard>
            );
          })
        )}
      </DocumentList>
    </DocumentsContainer>
  );
};

export default DocumentManager;
