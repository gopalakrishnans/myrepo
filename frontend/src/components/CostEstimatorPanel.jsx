import { useState, useMemo } from 'react';
import { calculateOutOfPocket } from '../utils/oopCalculator';

export default function CostEstimatorPanel({ prices }) {
  const [useInsurance, setUseInsurance] = useState(true);
  const [deductible, setDeductible] = useState(1500);
  const [deductibleMet, setDeductibleMet] = useState(0);
  const [coinsurancePct, setCoinsurancePct] = useState(20);
  const [oopMax, setOopMax] = useState(8000);
  const [selectedHospitalId, setSelectedHospitalId] = useState('');
  const [selectedPayerIdx, setSelectedPayerIdx] = useState('');

  const hospitals = useMemo(() => {
    const map = new Map();
    prices.forEach((p) => {
      if (!map.has(p.hospital_id)) {
        map.set(p.hospital_id, p.hospital_name);
      }
    });
    return Array.from(map, ([id, name]) => ({ id, name }));
  }, [prices]);

  const hospitalId = selectedHospitalId || (hospitals[0]?.id ?? '');

  const payerRates = useMemo(() => {
    return prices.filter(
      (p) => p.hospital_id === Number(hospitalId) && p.payer_name && p.negotiated_rate,
    );
  }, [prices, hospitalId]);

  const cashPrice = useMemo(() => {
    const row = prices.find(
      (p) => p.hospital_id === Number(hospitalId) && p.discounted_cash_price,
    );
    return row ? Number(row.discounted_cash_price) : null;
  }, [prices, hospitalId]);

  const allowedAmount = useMemo(() => {
    if (!useInsurance) return cashPrice;
    const idx = Number(selectedPayerIdx);
    if (payerRates[idx]) return Number(payerRates[idx].negotiated_rate);
    if (payerRates[0]) return Number(payerRates[0].negotiated_rate);
    return cashPrice;
  }, [useInsurance, cashPrice, payerRates, selectedPayerIdx]);

  const result = useMemo(() => {
    if (allowedAmount == null || allowedAmount <= 0) return null;
    if (!useInsurance) {
      return {
        allowedAmount,
        patientDeductiblePortion: 0,
        patientCoinsurance: 0,
        totalPatientCost: allowedAmount,
        insurancePays: 0,
      };
    }
    return calculateOutOfPocket({
      allowedAmount,
      deductible,
      deductibleMet,
      coinsurancePct,
      oopMax,
    });
  }, [allowedAmount, useInsurance, deductible, deductibleMet, coinsurancePct, oopMax]);

  const inputStyle = {
    padding: '0.4rem',
    border: '1px solid var(--color-gray-200)',
    borderRadius: 'var(--radius)',
    width: '100%',
    fontSize: '0.9rem',
  };
  const labelStyle = {
    display: 'block',
    fontSize: '0.8rem',
    color: 'var(--color-gray-500)',
    marginBottom: '0.15rem',
  };

  return (
    <div
      style={{
        background: 'white',
        borderRadius: 'var(--radius)',
        padding: '1.5rem',
        boxShadow: 'var(--shadow)',
        marginTop: '1.5rem',
      }}
    >
      <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
        Estimate Your Out-of-Pocket Cost
      </h3>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ flex: '1 1 200px' }}>
          <label style={labelStyle}>Hospital</label>
          <select
            value={hospitalId}
            onChange={(e) => {
              setSelectedHospitalId(e.target.value);
              setSelectedPayerIdx('');
            }}
            style={inputStyle}
          >
            {hospitals.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'flex-end' }}>
          <label style={{ fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={useInsurance}
              onChange={(e) => setUseInsurance(e.target.checked)}
            />
            I have insurance
          </label>
        </div>
      </div>

      {useInsurance && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ flex: '1 1 200px' }}>
            <label style={labelStyle}>Insurance Plan</label>
            <select
              value={selectedPayerIdx}
              onChange={(e) => setSelectedPayerIdx(e.target.value)}
              style={inputStyle}
            >
              {payerRates.length === 0 && <option value="">No plans available</option>}
              {payerRates.map((p, i) => (
                <option key={i} value={i}>
                  {p.payer_name} — ${Number(p.negotiated_rate).toLocaleString()}
                </option>
              ))}
            </select>
          </div>
          <div style={{ flex: '0 0 120px' }}>
            <label style={labelStyle}>Deductible ($)</label>
            <input
              type="number"
              min="0"
              value={deductible}
              onChange={(e) => setDeductible(Number(e.target.value))}
              style={inputStyle}
            />
          </div>
          <div style={{ flex: '0 0 120px' }}>
            <label style={labelStyle}>Deductible Met ($)</label>
            <input
              type="number"
              min="0"
              value={deductibleMet}
              onChange={(e) => setDeductibleMet(Number(e.target.value))}
              style={inputStyle}
            />
          </div>
          <div style={{ flex: '0 0 100px' }}>
            <label style={labelStyle}>Coinsurance (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={coinsurancePct}
              onChange={(e) => setCoinsurancePct(Number(e.target.value))}
              style={inputStyle}
            />
          </div>
          <div style={{ flex: '0 0 120px' }}>
            <label style={labelStyle}>OOP Max ($)</label>
            <input
              type="number"
              min="0"
              value={oopMax}
              onChange={(e) => setOopMax(Number(e.target.value))}
              style={inputStyle}
            />
          </div>
        </div>
      )}

      {result && (
        <div
          style={{
            background: 'var(--color-gray-50)',
            borderRadius: 'var(--radius)',
            padding: '1.25rem',
            marginTop: '0.5rem',
          }}
        >
          {useInsurance && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                <span style={{ color: 'var(--color-gray-500)' }}>Allowed amount (negotiated rate)</span>
                <span>${result.allowedAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                <span style={{ color: 'var(--color-gray-500)' }}>You pay toward deductible</span>
                <span>${result.patientDeductiblePortion.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                <span style={{ color: 'var(--color-gray-500)' }}>You pay coinsurance ({coinsurancePct}%)</span>
                <span>${result.patientCoinsurance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
              <hr style={{ border: 'none', borderTop: '1px solid var(--color-gray-200)', margin: '0.5rem 0' }} />
            </>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.35rem' }}>
            <span>Your estimated cost</span>
            <span style={{ color: 'var(--color-success)' }}>
              ${result.totalPatientCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
          {useInsurance && (
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--color-gray-500)' }}>Insurance covers</span>
              <span>${result.insurancePays.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          )}

          {useInsurance && result.allowedAmount > 0 && (
            <div
              style={{
                display: 'flex',
                height: '8px',
                borderRadius: '4px',
                overflow: 'hidden',
                marginTop: '0.75rem',
              }}
            >
              <div
                style={{
                  width: `${(result.totalPatientCost / result.allowedAmount) * 100}%`,
                  background: 'var(--color-primary)',
                }}
              />
              <div
                style={{
                  flex: 1,
                  background: 'var(--color-gray-200)',
                }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
