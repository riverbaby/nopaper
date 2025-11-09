import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'

interface Document {
  id: string
  title: string
  status: string
  page_count: number
  created_at: string
}

function DocumentList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await api.get('/documents')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading documents</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Documents</h2>
        <Link to="/upload" style={{ padding: '0.75rem 1.5rem', background: '#2c3e50', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
          Upload New
        </Link>
      </div>

      <div className="document-grid">
        {data?.documents?.map((doc: Document) => (
          <Link to={`/documents/${doc.id}`} key={doc.id} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="document-card">
              <h3>{doc.title}</h3>
              <p>Pages: {doc.page_count}</p>
              <span className={`status ${doc.status}`}>{doc.status}</span>
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
                {new Date(doc.created_at).toLocaleDateString()}
              </p>
            </div>
          </Link>
        ))}
      </div>

      {data?.documents?.length === 0 && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
          <p>No documents yet. Upload your first document to get started!</p>
        </div>
      )}
    </div>
  )
}

export default DocumentList
