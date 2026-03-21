import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { comparePrices, getProcedure } from '../api/client';

function formatPrice(value) {
  if (value == null) return '-';
  return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function ComparePage() {
  const [searchParams] = useSearchParams();
  const procedureId = searchParams.get('procedure_id');
  const hospitalIds = (searchParams.get('hospitals') || '').split(',').filter(Boolean);

  const { data: procedure } = useQuery({
    queryKey: ['procedure', procedureId],
    queryFn: () => getProcedure(procedureId),
    enabled: !!procedureId,
  });

  const { data: comparison, isLoading } = useQuery({
    queryKey: ['compare', procedureId, hospitalIds],
    queryFn: () => comparePrices(procedureId, hospitalIds),
    enabled: !!procedureId && hospitalIds.length >= 2,
  });

  if (!procedureId || hospitalIds.length < 2) {
    return (
      <div className="container" style={{ padding: '3rem 1rem', textAlign: 'center' }}>
        <h2>Compare Hospitals</h2>
        <p style={{ color: 'var(--color-gray-500)', marginTop: '1rem' }}>
          Select a procedure and at least 2 hospitals to compare prices.
        </p>
        <Link to="/" style={{ marginTop: '1rem', display: 'inline-block' }}>
          Go to Search
        </Link>
      </div>
    );
  }

  if (isLoading) return <div className="loading">Loading comparison...</div>;

  const hospitals = comparison?.hospitals || [];

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <Link to={procedure ? `/procedure/${procedureId}` : '/search'} style={{ fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>
        &larr; Back
      </Link>

      <h1 style={{ fontSize: '1.5rem', margin: '1rem 0' }}>
        Price Comparison: {comparison?.procedure_name || 'Loading...'}
      </h1>

      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${hospitals.length}, 1fr)`,
        gap: '1rem',
        marginTop: '1.5rem',
      }}>
        {hospitals.map((h) => (
          <div key={h.hospital_id} style={{
            background: 'white',
            borderRadius: 'var(--radius)',
            padding: '1.5rem',
            boxShadow: 'var(--shadow)',
          }}>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.25rem' }}>{h.hospital_name}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '1rem' }}>
              {h.city}, {h.state}
            </p>

            <div style={{ borderTop: '1px solid var(--color-gray-100)', paddingTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span style={{ color: 'var(--color-gray-500)', fontSize: '0.85rem' }}>Cash Price</span>
                <span style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-primary)' }}>
                  {formatPrice(h.cash_price)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ color: 'var(--color-gray-500)', fontSize: '0.85rem' }}>List Price</span>
                <span style={{ color: 'var(--color-gray-500)' }}>{formatPrice(h.gross_charge)}</span>
              </div>

              {h.payer_rates.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-gray-500)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                    Insurance Rates
                  </div>
                  {h.payer_rates.map((rate, i) => (
                    <div key={i} style={{
                      display: 'flex', justifyContent: 'space-between',
                      padding: '0.4rem 0', borderTop: '1px solid var(--color-gray-50)',
                      fontSize: '0.85rem',
                    }}>
                      <span style={{ color: 'var(--color-gray-700)' }}>
                        {rate.payer_name} <span style={{ color: 'var(--color-gray-400)' }}>({rate.plan_name})</span>
                      </span>
                      <span style={{ fontWeight: 600 }}>{formatPrice(rate.negotiated_rate)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
