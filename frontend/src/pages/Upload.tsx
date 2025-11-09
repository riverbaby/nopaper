import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

function Upload() {
  const [files, setFiles] = useState<FileList | null>(null)
  const navigate = useNavigate()

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData()
      Array.from(files).forEach(file => {
        formData.append('files', file)
      })

      const response = await api.post('/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: () => {
      navigate('/')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (files && files.length > 0) {
      uploadMutation.mutate(files)
    }
  }

  return (
    <div>
      <h2>Upload Documents</h2>

      <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
        <div className="upload-area">
          <input
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg,.tiff,.heic"
            onChange={(e) => setFiles(e.target.files)}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
            <div>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{ margin: '0 auto', color: '#2c3e50' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p style={{ marginTop: '1rem', fontSize: '1.125rem' }}>
                {files && files.length > 0 ? `${files.length} file(s) selected` : 'Click to select files'}
              </p>
              <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.875rem' }}>
                Supported: PDF, PNG, JPG, TIFF, HEIC
              </p>
            </div>
          </label>
        </div>

        {files && files.length > 0 && (
          <div style={{ marginTop: '1.5rem' }}>
            <h3>Selected Files:</h3>
            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
              {Array.from(files).map((file, idx) => (
                <li key={idx}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
          <button
            type="submit"
            disabled={!files || files.length === 0 || uploadMutation.isPending}
            style={{ padding: '0.75rem 2rem', background: '#2c3e50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1rem' }}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            style={{ padding: '0.75rem 2rem', background: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1rem' }}
          >
            Cancel
          </button>
        </div>

        {uploadMutation.isError && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
            Error uploading files. Please try again.
          </div>
        )}
      </form>
    </div>
  )
}

export default Upload
