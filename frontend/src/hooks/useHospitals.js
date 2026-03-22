import { useQuery } from '@tanstack/react-query';
import { searchHospitalsNearby } from '../api/client';

export function useNearbyHospitals(zipCode, radius, procedureId) {
  return useQuery({
    queryKey: ['nearbyHospitals', zipCode, radius, procedureId],
    queryFn: () =>
      searchHospitalsNearby({
        zip_code: zipCode,
        radius,
        procedure_id: procedureId,
      }),
    enabled: !!zipCode && zipCode.length === 5,
  });
}
