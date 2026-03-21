import { useQuery } from '@tanstack/react-query';
import { getPrices, getProcedureStats } from '../api/client';

export function usePrices(procedureId, filters = {}) {
  return useQuery({
    queryKey: ['prices', procedureId, filters],
    queryFn: () => getPrices({ procedure_id: procedureId, ...filters }),
    enabled: !!procedureId,
  });
}

export function useProcedureStats(procedureId) {
  return useQuery({
    queryKey: ['stats', procedureId],
    queryFn: () => getProcedureStats(procedureId),
    enabled: !!procedureId,
  });
}
