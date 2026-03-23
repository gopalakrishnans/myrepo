export function calculateOutOfPocket({
  allowedAmount,
  deductible,
  deductibleMet,
  coinsurancePct,
  oopMax,
}) {
  const remainingDeductible = Math.max(0, deductible - deductibleMet);
  const patientDeductiblePortion = Math.min(allowedAmount, remainingDeductible);
  const afterDeductible = allowedAmount - patientDeductiblePortion;
  const patientCoinsurance = afterDeductible * (coinsurancePct / 100);
  let totalPatientCost = patientDeductiblePortion + patientCoinsurance;

  if (oopMax > 0) {
    const remainingOopMax = Math.max(0, oopMax - deductibleMet);
    totalPatientCost = Math.min(totalPatientCost, remainingOopMax);
  }

  const insurancePays = allowedAmount - totalPatientCost;

  return {
    allowedAmount,
    patientDeductiblePortion,
    patientCoinsurance,
    totalPatientCost,
    insurancePays,
  };
}
