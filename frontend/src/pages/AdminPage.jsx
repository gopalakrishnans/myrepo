import { useState, useRef } from 'react';
import { uploadHospitalMrf } from '../api/client';

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState('');
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null); // null | 'uploading' | 'success' | 'error'
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file || !adminKey) return;

    setStatus('uploading');
    setResult(null);
    setErrorMsg('');

    try {
      const data = await uploadHospitalMrf(file, adminKey);
      setResult(data);
      setStatus('success');
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  }

  return (
    <div className="container" style={{ padding: '2rem 1rem', maxWidth: '600px' }}>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Admin — MRF Import</h1>
      <p style={{ color: 'var(--color-gray-500)', marginBottom: '1.5rem' }}>
        Upload a CMS hospital machine-readable file to ingest pricing data into the database.
        Accepts <code>.json</code> or <code>.json.gz</code> files.
      </p>

      <form onSubmit={handleSubmit} style={{
        background: 'white',
        borderRadius: 'var(--radius)',
        padding: '1.5rem',
        boxShadow: 'var(--shadow)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
            Admin Key
          </label>
          <input
            type="password"
            value={adminKey}
            onChange={(e) => setAdminKey(e.target.value)}
            placeholder="Enter ADMIN_SECRET"
            required
            style={{
              width: '100%',
              padding: '0.6rem',
              border: '1px solid var(--color-gray-200)',
              borderRadius: 'var(--radius)',
              fontSize: '1rem',
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-gray-500)', marginBottom: '0.25rem' }}>
            Hospital MRF File
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.json.gz"
            onChange={(e) => setFile(e.target.files[0] || null)}
            required
            style={{ fontSize: '0.95rem' }}
          />
          {file && (
            <div style={{ fontSize: '0.8rem', color: 'var(--color-gray-500)', marginTop: '0.25rem' }}>
              {file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={status === 'uploading' || !file || !adminKey}
          style={{
            padding: '0.65rem 1.25rem',
            background: 'var(--color-primary)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius)',
            fontSize: '1rem',
            cursor: status === 'uploading' ? 'not-allowed' : 'pointer',
            opacity: status === 'uploading' ? 0.7 : 1,
          }}
        >
          {status === 'uploading' ? 'Ingesting…' : 'Upload & Ingest'}
        </button>
      </form>

      {status === 'uploading' && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: '#f0f4ff',
          borderRadius: 'var(--radius)',
          color: 'var(--color-primary)',
        }}>
          Ingesting file — this may take a few minutes for large MRFs…
        </div>
      )}

      {status === 'success' && result && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: '#f0fdf4',
          border: '1px solid #86efac',
          borderRadius: 'var(--radius)',
        }}>
          <div style={{ fontWeight: 600, color: '#16a34a', marginBottom: '0.25rem' }}>Ingestion complete</div>
          <div style={{ fontSize: '0.9rem' }}>
            <strong>{result.records_ingested.toLocaleString()}</strong> price records ingested from <code>{result.filename}</code>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: '#fef2f2',
          border: '1px solid #fca5a5',
          borderRadius: 'var(--radius)',
          color: '#dc2626',
        }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}
    </div>
  );
}
