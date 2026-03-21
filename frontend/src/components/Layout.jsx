import { Link, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div>
      <header style={{
        background: 'white',
        borderBottom: '1px solid var(--color-gray-200)',
        padding: '1rem 0',
      }}>
        <div className="container" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <Link to="/" style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            color: 'var(--color-primary)',
            textDecoration: 'none',
          }}>
            ClearPrice Health
          </Link>
          <nav style={{ display: 'flex', gap: '1.5rem' }}>
            <Link to="/">Search</Link>
            <Link to="/search?category=Imaging">Imaging</Link>
            <Link to="/search?category=Lab">Lab</Link>
            <Link to="/search?category=Surgery">Surgery</Link>
          </nav>
        </div>
      </header>
      <main style={{ minHeight: 'calc(100vh - 140px)' }}>
        <Outlet />
      </main>
      <footer style={{
        background: 'white',
        borderTop: '1px solid var(--color-gray-200)',
        padding: '1.5rem 0',
        textAlign: 'center',
        color: 'var(--color-gray-500)',
        fontSize: '0.85rem',
      }}>
        <div className="container">
          Data sourced from hospital machine-readable files. Prices are estimates and may vary.
        </div>
      </footer>
    </div>
  );
}
