import { Routes, Route, Link } from 'react-router-dom'
import DocumentList from './pages/DocumentList'
import DocumentDetail from './pages/DocumentDetail'
import Upload from './pages/Upload'
import Search from './pages/Search'
import Chat from './pages/Chat'

function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <div className="container">
          <h1 className="logo">DocNest</h1>
          <div className="nav-links">
            <Link to="/">Documents</Link>
            <Link to="/upload">Upload</Link>
            <Link to="/search">Search</Link>
            <Link to="/chat">Chat</Link>
          </div>
        </div>
      </nav>

      <main className="container main-content">
        <Routes>
          <Route path="/" element={<DocumentList />} />
          <Route path="/documents/:id" element={<DocumentDetail />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/search" element={<Search />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
