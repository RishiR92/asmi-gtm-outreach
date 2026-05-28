import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', icon: '📊', label: 'Dashboard', end: true },
  { to: '/leads', icon: '👥', label: 'Leads' },
  { to: '/templates', icon: '✉️', label: 'Templates' },
  { to: '/queue', icon: '📬', label: 'Follow-ups' },
]

export default function Navbar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>Asmi Outreach</h1>
        <p>GTM Engine</p>
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
        Built for Asmi GTM
      </div>
    </aside>
  )
}
