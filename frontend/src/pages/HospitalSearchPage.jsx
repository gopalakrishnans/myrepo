import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchProcedures } from '../api/client';
import { useNearbyHospitals } from '../hooks/useHospitals';

export default function HospitalSearchPage() {
  const [searchParams] = useSearchParams();
  const [zipCode, setZipCode] = useState('');
  const [radius, setRadius] = useState('');
  const [procedureId, setProcedureId] = useState(searchParams.get('procedure_id') || '');
  const [procedureQuery, setProcedureQuery] = useState('');
  const [submittedZip, setSubmittedZip] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const { data: suggestions } = useQuery({
    queryKey: ['procedureSearch', procedureQuery],
    queryFn: () => searchProcedures({ q: procedureQuery, limit: 5 }),
    enabled: procedureQuery.length >= 2,
  });

  const { data, isLoading, error } = useNearbyHospitals(
    submittedZip,
    radius || undefined,
    procedureId || undefined,
  );

  const handleSearch = (e) => {
    e.preventDefault();
    if (zipCode.length === 5) {
      setSubmittedZip(zipCode);
    }
  };

  return (
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Find Hospitals Near You</h1>

      <form
        onSubmit={handleSearch}
        style={{
          background: 'white',
          borderRadius: 'var(--radius)',
          padding: '1.5rem',
          boxShadow: 'var(--shadow)',
          marginBottom: '1.5rem',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '1rem',
          alignItems: 'flex-end',
        }}
      >
        <div style={{ flex: '0 0 140px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
            ZIP Code
          </label>
          <input
            type="text"
            value={zipCode}
            onChange={(e) => setZipCode(e.target.value.replace(/\D/g, '').slice(0, 5))}
            placeholder="e.g. 90012"
            style={{
              padding: '0.5rem',
              border: '1px solid var(--color-gray-200)',
              borderRadius: 'var(--radius)',
              width: '100%',
              fontSize: '0.9rem',
            }}
          />
        </div>

        <div style={{ flex: '0 0 160px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
            Radius
          </label>
          <select
            value={radius}
            onChange={(e) => setRadius(e.target.value)}
            style={{
              padding: '0.5rem',
              border: '1px solid var(--color-gray-200)',
              borderRadius: 'var(--radius)',
              width: '100%',
              fontSize: '0.9rem',
            }}
          >
            <option value="">Any distance</option>
            <option value="10">10 miles</option>
            <option value="25">25 miles</option>
            <option value="50">50 miles</option>
            <option value="100">100 miles</option>
          </select>
        </div>

        <div style={{ flex: '1 1 200px', position: 'relative' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
            Procedure (optional)
          </label>
          <input
            type="text"
            value={procedureQuery}
            onChange={(e) => {
              setProcedureQuery(e.target.value);
              setProcedureId('');
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Search procedures..."
            style={{
              padding: '0.5rem',
              border: '1px solid var(--color-gray-200)',
              borderRadius: 'var(--radius)',
              width: '100%',
              fontSize: '0.9rem',
            }}
          />
          {showSuggestions && suggestions?.items?.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
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
                    setProcedureId(String(proc.id));
                    setProcedureQuery(proc.plain_language_name || proc.description);
                    setShowSuggestions(false);
                  }}
                  style={{
                    padding: '0.5rem 0.75rem',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    borderBottom: '1px solid var(--color-gray-100)',
                  }}
                >
                  {proc.plain_language_name || proc.description}
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={zipCode.length !== 5}
          style={{
            padding: '0.5rem 1.5rem',
            background: zipCode.length === 5 ? 'var(--color-primary)' : 'var(--color-gray-300)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius)',
            cursor: zipCode.length === 5 ? 'pointer' : 'not-allowed',
            fontSize: '0.9rem',
            fontWeight: 600,
          }}
        >
          Search
        </button>
      </form>

      {error && (
        <div style={{ color: 'var(--color-danger)', marginBottom: '1rem' }}>
          {error.message}
        </div>
      )}

      {isLoading && <div className="loading">Searching hospitals...</div>}

      {data && (
        <>
          <p style={{ color: 'var(--color-gray-500)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            {data.total} hospital{data.total !== 1 ? 's' : ''} found
          </p>
          <div style={{
            background: 'white',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow)',
            overflow: 'hidden',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-gray-200)', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>Hospital</th>
                  <th style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>City</th>
                  <th style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>State</th>
                  <th style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--color-gray-500)' }}>ZIP</th>
                  <th style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--color-gray-500)', textAlign: 'right' }}>Distance</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((h) => (
                  <tr key={h.id} style={{ borderBottom: '1px solid var(--color-gray-100)' }}>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                      {procedureId ? (
                        <Link to={`/procedure/${procedureId}`}>{h.name}</Link>
                      ) : (
                        h.name
                      )}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-gray-600)' }}>{h.city}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-gray-600)' }}>{h.state}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-gray-600)' }}>{h.zip_code}</td>
                    <td style={{ padding: '0.75rem 1rem', textAlign: 'right', fontWeight: 600, color: 'var(--color-primary)' }}>
                      {h.distance_miles} mi
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
