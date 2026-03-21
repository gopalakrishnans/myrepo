import FairPriceBadge from './FairPriceBadge';
import styles from '../styles/components/PriceCard.module.css';

function formatPrice(value) {
  if (value == null) return 'N/A';
  return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function PriceCard({ price, fairPrice }) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <div className={styles.hospitalName}>{price.hospital_name}</div>
          <div className={styles.location}>
            {price.hospital_city}, {price.hospital_state}
          </div>
        </div>
        <FairPriceBadge price={price.discounted_cash_price} fairPrice={fairPrice} />
      </div>
      <div className={styles.priceRow}>
        <span className={styles.priceLabel}>Cash Price</span>
        <span className={`${styles.priceValue} ${styles.cashPrice}`}>
          {formatPrice(price.discounted_cash_price)}
        </span>
      </div>
      {price.negotiated_rate && (
        <div className={styles.priceRow}>
          <span className={styles.priceLabel}>
            {price.payer_name} ({price.plan_name})
          </span>
          <span className={`${styles.priceValue} ${styles.negotiatedPrice}`}>
            {formatPrice(price.negotiated_rate)}
          </span>
        </div>
      )}
      {price.min_negotiated_rate && price.max_negotiated_rate && (
        <div className={styles.priceRow}>
          <span className={styles.priceLabel}>Insured Range</span>
          <span className={styles.rangeText}>
            {formatPrice(price.min_negotiated_rate)} - {formatPrice(price.max_negotiated_rate)}
          </span>
        </div>
      )}
    </div>
  );
}
