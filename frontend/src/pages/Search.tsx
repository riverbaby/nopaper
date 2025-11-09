import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'

function Search() {
  const [query, setQuery] = useState('')

  const searchMutation = useMutation({
    mutationFn: async (q: string) => {
      const response = await api.post('/search/', {
        q,
        k: 20,
        hybrid: true,
      })
      return response.data
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      searchMutation.mutate(query)
    }
  }

  return (
    <div>
      <h2>Search Documents</h2>

      <form onSubmit={handleSearch} className="search-box">
        <input
          type="text"
          placeholder="Search for documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={searchMutation.isPending}>
          {searchMutation.isPending ? 'Searching...' : 'Search'}
        </button>
      </form>

      {searchMutation.isSuccess && (
        <div>
          <p style={{ marginBottom: '1rem', color: '#666' }}>
            Found {searchMutation.data.total} result(s)
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {searchMutation.data.results.map((result: any, idx: number) => (
              <div key={idx} style={{ background: 'white', padding: '1.5rem', borderRadius: '8px' }}>
                <Link to={`/documents/${result.document_id}`} style={{ textDecoration: 'none', color: '#2c3e50' }}>
                  <h3>{result.title}</h3>
                </Link>
                {result.page_index !== null && (
                  <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.875rem' }}>
                    Page {result.page_index + 1}
                  </p>
                )}
                <p style={{ marginTop: '0.5rem', color: '#333' }}>{result.excerpt}</p>
                <p style={{ marginTop: '0.5rem', color: '#999', fontSize: '0.875rem' }}>
                  Score: {result.score.toFixed(3)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {searchMutation.isError && (
        <div style={{ padding: '1rem', background: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
          Error performing search. Please try again.
        </div>
      )}
    </div>
  )
}

export default Search
