import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { searchProcedures } from '../api/client';

export function useSearch(initialQuery = '', category = '') {
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(initialQuery), 300);
    return () => clearTimeout(timer);
  }, [initialQuery]);

  return useQuery({
    queryKey: ['procedures', debouncedQuery, category],
    queryFn: () => searchProcedures({ q: debouncedQuery, category, limit: 50 }),
    enabled: debouncedQuery.length > 0 || category.length > 0,
  });
}
