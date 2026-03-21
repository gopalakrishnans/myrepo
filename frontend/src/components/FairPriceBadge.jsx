export default function FairPriceBadge({ price, fairPrice }) {
  if (!price || !fairPrice) return null;

  const ratio = price / fairPrice;
  let label, color, bg;

  if (ratio <= 0.85) {
    label = 'Great Price';
    color = '#16a34a';
    bg = '#f0fdf4';
  } else if (ratio <= 1.15) {
    label = 'Fair Price';
    color = '#2563eb';
    bg = '#eff6ff';
  } else {
    label = 'Above Average';
    color = '#d97706';
    bg = '#fffbeb';
  }

  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 10px',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 600,
      color,
      background: bg,
    }}>
      {label}
    </span>
  );
}
