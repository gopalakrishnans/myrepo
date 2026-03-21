import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import { searchProcedures, getProcedureStats } from '../api/client';

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const q = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';
  const [filters, setFilters] = useState({ category: categoryParam, state: '' });

  const { data, isLoading } = useQuery({
    queryKey: ['searchResults', q, filters.category],
    queryFn: () => searchProcedures({ q, category: filters.category, limit: 50 }),
  });

  const procedures = data?.items || [];

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <SearchBar initialValue={q} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '1.5rem' }}>
        <aside>
          <FilterPanel filters={filters} onFilterChange={setFilters} />
        </aside>

        <div>
          {isLoading && <div className="loading">Searching...</div>}

          {!isLoading && procedures.length === 0 && (
            <div className="empty">
              No procedures found. Try a different search term.
            </div>
          )}

          {!isLoading && procedures.length > 0 && (
            <>
              <p style={{ color: 'var(--color-gray-500)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                {data.total} procedure{data.total !== 1 ? 's' : ''} found
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {procedures.map((proc) => (
                  <ProcedureResultCard key={proc.id} procedure={proc} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ProcedureResultCard({ procedure }) {
  const { data: stats } = useQuery({
    queryKey: ['quickStats', procedure.id],
    queryFn: () => getProcedureStats(procedure.id),
  });

  return (
    <Link
      to={`/procedure/${procedure.id}`}
      style={{
        display: 'block',
        background: 'white',
        borderRadius: 'var(--radius)',
        padding: '1.25rem',
        boxShadow: 'var(--shadow)',
        textDecoration: 'none',
        color: 'inherit',
        transition: 'box-shadow 0.2s',
      }}
      onMouseEnter={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-lg)'}
      onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'var(--shadow)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.25rem' }}>
            {procedure.plain_language_name}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>
            {procedure.code_type} {procedure.billing_code}
            <span style={{
              marginLeft: '0.75rem',
              background: 'rgba(37, 99, 235, 0.08)',
              color: 'var(--color-primary)',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '0.75rem',
            }}>
              {procedure.category}
            </span>
          </div>
        </div>
        {stats && stats.fair_price && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)' }}>Fair Price</div>
            <div style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--color-primary)' }}>
              ${Math.round(stats.fair_price).toLocaleString()}
            </div>
            {stats.cash_price_min != null && (
              <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)' }}>
                ${Math.round(stats.cash_price_min).toLocaleString()} - ${Math.round(stats.cash_price_max).toLocaleString()}
              </div>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}
