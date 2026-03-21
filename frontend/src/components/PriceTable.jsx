import { useState } from 'react';
import FairPriceBadge from './FairPriceBadge';
import styles from '../styles/components/PriceTable.module.css';

function formatPrice(value) {
  if (value == null) return '-';
  return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function PriceTable({ prices, fairPrice }) {
  const [sortField, setSortField] = useState('discounted_cash_price');
  const [sortAsc, setSortAsc] = useState(true);

  // Only show cash-price rows (one per hospital)
  const cashPrices = prices.filter(p => !p.payer_name);

  const sorted = [...cashPrices].sort((a, b) => {
    const aVal = a[sortField] ?? Infinity;
    const bVal = b[sortField] ?? Infinity;
    return sortAsc ? aVal - bVal : bVal - aVal;
  });

  function handleSort(field) {
    if (field === sortField) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  }

  const arrow = (field) => sortField === field ? (sortAsc ? ' ↑' : ' ↓') : '';

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th onClick={() => handleSort('hospital_name')}>
              Hospital{arrow('hospital_name')}
            </th>
            <th>Location</th>
            <th onClick={() => handleSort('discounted_cash_price')}>
              Cash Price{arrow('discounted_cash_price')}
            </th>
            <th onClick={() => handleSort('gross_charge')}>
              List Price{arrow('gross_charge')}
            </th>
            <th>Insured Range</th>
            <th>Rating</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((p) => (
            <tr key={p.id}>
              <td style={{ fontWeight: 500 }}>{p.hospital_name}</td>
              <td>{p.hospital_city}, {p.hospital_state}</td>
              <td className={styles.priceCell}>{formatPrice(p.discounted_cash_price)}</td>
              <td style={{ color: 'var(--color-gray-500)' }}>{formatPrice(p.gross_charge)}</td>
              <td>
                {p.min_negotiated_rate
                  ? `${formatPrice(p.min_negotiated_rate)} - ${formatPrice(p.max_negotiated_rate)}`
                  : '-'}
              </td>
              <td><FairPriceBadge price={p.discounted_cash_price} fairPrice={fairPrice} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
