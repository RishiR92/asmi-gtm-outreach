import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Dashboard from './components/Dashboard.jsx'
import Leads from './components/Leads.jsx'
import Templates from './components/Templates.jsx'
import SendQueue from './components/SendQueue.jsx'

export default function App() {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/queue" element={<SendQueue />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
