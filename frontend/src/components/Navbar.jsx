import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', icon: '📊', label: 'Dashboard', end: true },
  { to: '/leads', icon: '👥', label: 'Leads' },
  { to: '/finder', icon: '🔍', label: 'Email Finder' },
  { to: '/templates', icon: '✉️', label: 'Templates' },
  { to: '/queue', icon: '📬', label: 'Send Queue' },
  { to: '/settings', icon: '⚙️', label: 'Settings' },
]

export default function Navbar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>Cold Outreach</h1>
        <p>Asmi Newsletter System</p>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        Built for Asmi outreach
      </div>
    </aside>
  )
}
