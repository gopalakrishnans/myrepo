import { describe, it, expect } from 'vitest';
import { calculateOutOfPocket } from './oopCalculator';

describe('calculateOutOfPocket', () => {
  it('calculates cost when deductible is not met', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1000,
      deductible: 500,
      deductibleMet: 0,
      coinsurancePct: 20,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(500);
    expect(result.patientCoinsurance).toBe(100); // 20% of (1000 - 500)
    expect(result.totalPatientCost).toBe(600);
    expect(result.insurancePays).toBe(400);
  });

  it('calculates cost when deductible is fully met', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1000,
      deductible: 500,
      deductibleMet: 500,
      coinsurancePct: 20,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(0);
    expect(result.patientCoinsurance).toBe(200); // 20% of 1000
    expect(result.totalPatientCost).toBe(200);
    expect(result.insurancePays).toBe(800);
  });

  it('calculates cost when deductible is partially met', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1000,
      deductible: 500,
      deductibleMet: 300,
      coinsurancePct: 20,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(200);
    expect(result.patientCoinsurance).toBe(160); // 20% of (1000 - 200)
    expect(result.totalPatientCost).toBe(360);
    expect(result.insurancePays).toBe(640);
  });

  it('caps cost at OOP maximum', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 10000,
      deductible: 2000,
      deductibleMet: 0,
      coinsurancePct: 30,
      oopMax: 3000,
    });

    // Without cap: 2000 + 30% of 8000 = 2000 + 2400 = 4400
    // Remaining OOP max: 3000 - 0 = 3000
    expect(result.totalPatientCost).toBe(3000);
    expect(result.insurancePays).toBe(7000);
  });

  it('accounts for deductibleMet in OOP max calculation', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 5000,
      deductible: 1000,
      deductibleMet: 800,
      coinsurancePct: 20,
      oopMax: 1500,
    });

    // Remaining deductible: 200
    // After deductible: 4800
    // Coinsurance: 20% of 4800 = 960
    // Raw total: 200 + 960 = 1160
    // Remaining OOP: 1500 - 800 = 700
    expect(result.totalPatientCost).toBe(700);
  });

  it('handles zero coinsurance', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1000,
      deductible: 500,
      deductibleMet: 0,
      coinsurancePct: 0,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(500);
    expect(result.patientCoinsurance).toBe(0);
    expect(result.totalPatientCost).toBe(500);
    expect(result.insurancePays).toBe(500);
  });

  it('handles zero deductible', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1000,
      deductible: 0,
      deductibleMet: 0,
      coinsurancePct: 20,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(0);
    expect(result.patientCoinsurance).toBe(200);
    expect(result.totalPatientCost).toBe(200);
  });

  it('handles cost less than deductible', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 100,
      deductible: 500,
      deductibleMet: 0,
      coinsurancePct: 20,
      oopMax: 5000,
    });

    expect(result.patientDeductiblePortion).toBe(100);
    expect(result.patientCoinsurance).toBe(0);
    expect(result.totalPatientCost).toBe(100);
    expect(result.insurancePays).toBe(0);
  });

  it('handles no OOP max (oopMax = 0)', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 10000,
      deductible: 2000,
      deductibleMet: 0,
      coinsurancePct: 30,
      oopMax: 0,
    });

    // No OOP max cap applied
    expect(result.totalPatientCost).toBe(2000 + 2400); // 4400
    expect(result.insurancePays).toBe(5600);
  });

  it('returns the original allowedAmount', () => {
    const result = calculateOutOfPocket({
      allowedAmount: 1234.56,
      deductible: 0,
      deductibleMet: 0,
      coinsurancePct: 0,
      oopMax: 0,
    });

    expect(result.allowedAmount).toBe(1234.56);
  });
});
