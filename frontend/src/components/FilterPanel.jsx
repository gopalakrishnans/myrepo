import { useQuery } from '@tanstack/react-query';
import { getCategories } from '../api/client';

const STATES = ['CA', 'NY', 'TX', 'FL', 'IL'];

export default function FilterPanel({ filters, onFilterChange }) {
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  return (
    <div style={{
      background: 'white',
      borderRadius: 'var(--radius)',
      padding: '1.25rem',
      boxShadow: 'var(--shadow)',
    }}>
      <h3 style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--color-gray-700)' }}>
        Filters
      </h3>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-gray-500)', display: 'block', marginBottom: '0.5rem' }}>
          Category
        </label>
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
          style={{
            width: '100%', padding: '0.5rem', borderRadius: 'var(--radius)',
            border: '1px solid var(--color-gray-200)', fontSize: '0.9rem',
          }}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-gray-500)', display: 'block', marginBottom: '0.5rem' }}>
          State
        </label>
        <select
          value={filters.state || ''}
          onChange={(e) => onFilterChange({ ...filters, state: e.target.value })}
          style={{
            width: '100%', padding: '0.5rem', borderRadius: 'var(--radius)',
            border: '1px solid var(--color-gray-200)', fontSize: '0.9rem',
          }}
        >
          <option value="">All States</option>
          {STATES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {(filters.category || filters.state) && (
        <button
          onClick={() => onFilterChange({ category: '', state: '' })}
          style={{
            width: '100%', padding: '0.5rem', background: 'var(--color-gray-100)',
            border: 'none', borderRadius: 'var(--radius)', fontSize: '0.85rem',
            color: 'var(--color-gray-700)',
          }}
        >
          Clear Filters
        </button>
      )}
    </div>
  );
}
