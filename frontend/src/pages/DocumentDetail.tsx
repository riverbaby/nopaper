import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import api from '../api/client'

function DocumentDetail() {
  const { id } = useParams()

  const { data, isLoading, error } = useQuery({
    queryKey: ['document', id],
    queryFn: async () => {
      const response = await api.get(`/documents/${id}`)
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading document</div>

  return (
    <div>
      <Link to="/" style={{ marginBottom: '1rem', display: 'inline-block' }}>← Back to Documents</Link>

      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', marginTop: '1rem' }}>
        <h2>{data?.title}</h2>
        <div style={{ margin: '1rem 0' }}>
          <span className={`status ${data?.status}`}>{data?.status}</span>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <h3>Summary</h3>
          {data?.summary?.summary_md ? (
            <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
              <pre style={{ whiteSpace: 'pre-wrap' }}>{data.summary.summary_md}</pre>
            </div>
          ) : (
            <p style={{ color: '#666' }}>No summary available</p>
          )}
        </div>

        {data?.summary?.keywords && data.summary.keywords.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <h3>Keywords</h3>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
              {data.summary.keywords.map((keyword: string, idx: number) => (
                <span key={idx} style={{ padding: '0.25rem 0.75rem', background: '#e3f2fd', borderRadius: '4px', fontSize: '0.875rem' }}>
                  #{keyword}
                </span>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: '2rem' }}>
          <h3>Pages ({data?.page_count})</h3>
          <div style={{ marginTop: '1rem' }}>
            {data?.pages?.map((page: any, idx: number) => (
              <details key={idx} style={{ marginBottom: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
                <summary style={{ cursor: 'pointer', fontWeight: '500' }}>Page {idx + 1}</summary>
                <div style={{ marginTop: '1rem', whiteSpace: 'pre-wrap' }}>
                  {page.ocr_text || 'No OCR text available'}
                </div>
              </details>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentDetail
