import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProcedure, getPrices, getProcedureStats } from '../api/client';
import PriceTable from '../components/PriceTable';

export default function ProcedureDetailPage() {
  const { id } = useParams();
  const [stateFilter, setStateFilter] = useState('');

  const { data: procedure, isLoading: procLoading } = useQuery({
    queryKey: ['procedure', id],
    queryFn: () => getProcedure(id),
  });

  const { data: pricesData, isLoading: pricesLoading } = useQuery({
    queryKey: ['procedurePrices', id, stateFilter],
    queryFn: () => getPrices({ procedure_id: id, state: stateFilter, limit: 200 }),
    enabled: !!id,
  });

  const { data: stats } = useQuery({
    queryKey: ['procedureStats', id],
    queryFn: () => getProcedureStats(id),
    enabled: !!id,
  });

  if (procLoading) return <div className="loading">Loading...</div>;
  if (!procedure) return <div className="error">Procedure not found</div>;

  const prices = pricesData?.items || [];

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <Link to="/search" style={{ fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>
        &larr; Back to search
      </Link>

      <div style={{
        background: 'white',
        borderRadius: 'var(--radius)',
        padding: '2rem',
        boxShadow: 'var(--shadow)',
        marginTop: '1rem',
        marginBottom: '1.5rem',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>
              {procedure.plain_language_name}
            </h1>
            <p style={{ color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
              {procedure.description}
            </p>
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
            <div style={{
              background: 'var(--color-gray-50)',
              borderRadius: 'var(--radius)',
              padding: '1.25rem',
              textAlign: 'center',
              minWidth: '180px',
            }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
                Fair Price (Median Cash)
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                ${Math.round(stats.fair_price).toLocaleString()}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-gray-500)', marginTop: '0.25rem' }}>
                Range: ${Math.round(stats.cash_price_min).toLocaleString()} - ${Math.round(stats.cash_price_max).toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)' }}>
                Based on {stats.cash_price_count} hospitals
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.2rem' }}>Price Comparison</h2>
        <select
          value={stateFilter}
          onChange={(e) => setStateFilter(e.target.value)}
          style={{
            padding: '0.5rem', borderRadius: 'var(--radius)',
            border: '1px solid var(--color-gray-200)', fontSize: '0.9rem',
          }}
        >
          <option value="">All States</option>
          <option value="CA">California</option>
          <option value="NY">New York</option>
          <option value="TX">Texas</option>
          <option value="FL">Florida</option>
          <option value="IL">Illinois</option>
        </select>
      </div>

      {pricesLoading ? (
        <div className="loading">Loading prices...</div>
      ) : prices.length === 0 ? (
        <div className="empty">No prices found for this filter.</div>
      ) : (
        <PriceTable prices={prices} fairPrice={stats?.fair_price} />
      )}

      {stats && (
        <div style={{
          background: 'white',
          borderRadius: 'var(--radius)',
          padding: '1.5rem',
          boxShadow: 'var(--shadow)',
          marginTop: '1.5rem',
        }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Price Statistics</h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '1rem',
          }}>
            <StatBox label="Average Cash Price" value={stats.cash_price_avg} />
            <StatBox label="Median Cash Price" value={stats.cash_price_median} />
            <StatBox label="Lowest Cash Price" value={stats.cash_price_min} accent />
            <StatBox label="Highest Cash Price" value={stats.cash_price_max} />
            <StatBox label="Avg Negotiated Rate" value={stats.negotiated_avg} />
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value, accent }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
        {label}
      </div>
      <div style={{
        fontSize: '1.4rem',
        fontWeight: 700,
        color: accent ? 'var(--color-success)' : 'var(--color-gray-900)',
      }}>
        {value != null ? `$${Math.round(value).toLocaleString()}` : '-'}
      </div>
    </div>
  );
}
