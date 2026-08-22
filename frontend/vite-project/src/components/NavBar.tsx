import Logo from './Logo'
import type { Page } from '../App'

const LINKS: { id: Page; label: string }[] = [
  { id: 'chat', label: 'Support chat' },
  { id: 'widget', label: 'Widget preview' },
  { id: 'inbox', label: 'Agent inbox' },
  { id: 'repairs', label: 'Repairs' },
  { id: 'admin', label: 'Admin settings' },
]

export default function NavBar({ page, onNavigate }: { page: Page; onNavigate: (page: Page) => void }) {
  return (
    <header className="app-navbar">
      <Logo size={30} />
      <nav className="app-nav-links" aria-label="Main navigation">
        {LINKS.map((link) => (
          <button
            key={link.id}
            type="button"
            className={`app-nav-link ${page === link.id ? 'active' : ''}`}
            onClick={() => onNavigate(link.id)}
          >
            {link.label}
          </button>
        ))}
      </nav>
    </header>
  )
}
