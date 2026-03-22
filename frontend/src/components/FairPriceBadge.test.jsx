import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import FairPriceBadge from './FairPriceBadge';

describe('FairPriceBadge', () => {
  it('renders nothing when price is null', () => {
    const { container } = render(<FairPriceBadge price={null} fairPrice={100} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when fairPrice is null', () => {
    const { container } = render(<FairPriceBadge price={100} fairPrice={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('shows "Great Price" when price is <= 85% of fair price', () => {
    render(<FairPriceBadge price={80} fairPrice={100} />);
    expect(screen.getByText('Great Price')).toBeInTheDocument();
  });

  it('shows "Fair Price" when price is between 85% and 115% of fair price', () => {
    render(<FairPriceBadge price={100} fairPrice={100} />);
    expect(screen.getByText('Fair Price')).toBeInTheDocument();
  });

  it('shows "Above Average" when price is > 115% of fair price', () => {
    render(<FairPriceBadge price={120} fairPrice={100} />);
    expect(screen.getByText('Above Average')).toBeInTheDocument();
  });

  it('shows "Great Price" at exactly 85% boundary (<=0.85)', () => {
    render(<FairPriceBadge price={85} fairPrice={100} />);
    expect(screen.getByText('Great Price')).toBeInTheDocument();
  });

  it('shows "Fair Price" at exactly 115% boundary', () => {
    render(<FairPriceBadge price={115} fairPrice={100} />);
    expect(screen.getByText('Fair Price')).toBeInTheDocument();
  });

  it('shows "Great Price" just below 85% boundary', () => {
    render(<FairPriceBadge price={84} fairPrice={100} />);
    expect(screen.getByText('Great Price')).toBeInTheDocument();
  });

  it('shows "Above Average" just above 115% boundary', () => {
    render(<FairPriceBadge price={116} fairPrice={100} />);
    expect(screen.getByText('Above Average')).toBeInTheDocument();
  });
});
