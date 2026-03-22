import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { searchProcedures, getPrices } from '../api/client';
import CostEstimatorPanel from '../components/CostEstimatorPanel';

export default function EstimatorPage() {
  const [query, setQuery] = useState('');
  const [selectedProcedure, setSelectedProcedure] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const { data: suggestions } = useQuery({
    queryKey: ['procedureSearch', query],
    queryFn: () => searchProcedures({ q: query, limit: 5 }),
    enabled: query.length >= 2,
  });

  const { data: pricesData, isLoading: pricesLoading } = useQuery({
    queryKey: ['procedurePrices', selectedProcedure?.id],
    queryFn: () => getPrices({ procedure_id: selectedProcedure.id, limit: 200 }),
    enabled: !!selectedProcedure,
  });

  const prices = pricesData?.items || [];

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Cost Estimator</h1>
      <p style={{ color: 'var(--color-gray-500)', marginBottom: '1.5rem' }}>
        Estimate your out-of-pocket costs based on your insurance plan details.
      </p>

      <div style={{
        background: 'white',
        borderRadius: 'var(--radius)',
        padding: '1.5rem',
        boxShadow: 'var(--shadow)',
        marginBottom: '1.5rem',
        position: 'relative',
      }}>
        <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
          Search for a procedure
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSelectedProcedure(null);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="e.g. MRI, X-Ray, blood test..."
          style={{
            padding: '0.6rem',
            border: '1px solid var(--color-gray-200)',
            borderRadius: 'var(--radius)',
            width: '100%',
            fontSize: '1rem',
          }}
        />
        {showSuggestions && suggestions?.items?.length > 0 && (
          <div style={{
            position: 'absolute',
            left: '1.5rem',
            right: '1.5rem',
            background: 'white',
            border: '1px solid var(--color-gray-200)',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow)',
            zIndex: 10,
            maxHeight: '200px',
            overflow: 'auto',
          }}>
            {suggestions.items.map((proc) => (
              <div
                key={proc.id}
                onMouseDown={() => {
                  setSelectedProcedure(proc);
                  setQuery(proc.plain_language_name || proc.description);
                  setShowSuggestions(false);
                }}
                style={{
                  padding: '0.6rem 0.75rem',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  borderBottom: '1px solid var(--color-gray-100)',
                }}
              >
                <div style={{ fontWeight: 500 }}>{proc.plain_language_name || proc.description}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)' }}>
                  {proc.code_type} {proc.billing_code}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {pricesLoading && <div className="loading">Loading prices...</div>}

      {selectedProcedure && prices.length > 0 && (
        <CostEstimatorPanel prices={prices} />
      )}

      {selectedProcedure && !pricesLoading && prices.length === 0 && (
        <div className="empty">No pricing data available for this procedure.</div>
      )}
    </div>
  );
}
