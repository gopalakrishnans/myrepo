import { Link } from 'react-router-dom';
import SearchBar from '../components/SearchBar';

const CATEGORIES = [
  { name: 'Imaging', desc: 'MRI, CT Scan, X-Ray', color: '#3b82f6' },
  { name: 'Lab', desc: 'Blood Tests, Panels', color: '#10b981' },
  { name: 'Surgery', desc: 'Knee, Hip, Cataract', color: '#ef4444' },
  { name: 'Emergency', desc: 'ER Visits', color: '#f59e0b' },
  { name: 'Preventive', desc: 'Physicals, Screening', color: '#8b5cf6' },
  { name: 'Office Visit', desc: 'Doctor Visits', color: '#06b6d4' },
  { name: 'Maternity', desc: 'Delivery, C-Section', color: '#ec4899' },
  { name: 'Cardiac', desc: 'EKG, Echo', color: '#f97316' },
];

export default function HomePage() {
  return (
    <div>
      <section style={{
        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
        color: 'white',
        padding: '4rem 1rem',
        textAlign: 'center',
      }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.75rem' }}>
          Know Before You Go
        </h1>
        <p style={{ fontSize: '1.15rem', opacity: 0.9, marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
          Compare real hospital prices for medical procedures. No surprises.
        </p>
        <SearchBar autoFocus />
      </section>

      <section className="container" style={{ padding: '3rem 1rem' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--color-gray-700)' }}>
          Browse by Category
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '1rem',
          maxWidth: '900px',
          margin: '0 auto',
        }}>
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.name}
              to={`/search?category=${cat.name}`}
              style={{
                display: 'block',
                background: 'white',
                borderRadius: 'var(--radius)',
                padding: '1.25rem',
                textDecoration: 'none',
                boxShadow: 'var(--shadow)',
                borderLeft: `4px solid ${cat.color}`,
                transition: 'transform 0.15s, box-shadow 0.15s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = '';
                e.currentTarget.style.boxShadow = 'var(--shadow)';
              }}
            >
              <div style={{ fontWeight: 600, color: 'var(--color-gray-900)', marginBottom: '0.25rem' }}>
                {cat.name}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>
                {cat.desc}
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section style={{
        background: 'white',
        padding: '3rem 1rem',
        textAlign: 'center',
      }}>
        <div className="container" style={{ maxWidth: '800px' }}>
          <h2 style={{ marginBottom: '1rem', color: 'var(--color-gray-700)' }}>
            How It Works
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '2rem',
            marginTop: '2rem',
          }}>
            {[
              { step: '1', title: 'Search', desc: 'Find your procedure by name or code' },
              { step: '2', title: 'Compare', desc: 'See prices across hospitals near you' },
              { step: '3', title: 'Save', desc: 'Choose the best price and avoid surprises' },
            ].map((item) => (
              <div key={item.step}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '50%',
                  background: 'var(--color-primary)', color: 'white',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.25rem', fontWeight: 700, margin: '0 auto 0.75rem',
                }}>
                  {item.step}
                </div>
                <h3 style={{ marginBottom: '0.25rem' }}>{item.title}</h3>
                <p style={{ color: 'var(--color-gray-500)', fontSize: '0.9rem' }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
