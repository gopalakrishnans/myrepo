const BASE_URL = '/api/v1';

export async function fetchApi(path, params = {}) {
  const url = new URL(path, window.location.origin);
  url.pathname = BASE_URL + path;
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export function searchProcedures(params) {
  return fetchApi('/procedures/search', params);
}

export function getProcedure(id) {
  return fetchApi(`/procedures/${id}`);
}

export function getCategories() {
  return fetchApi('/procedures/categories');
}

export function getPrices(params) {
  return fetchApi('/prices', params);
}

export function comparePrices(procedureId, hospitalIds) {
  return fetchApi('/prices/compare', {
    procedure_id: procedureId,
    hospital_ids: hospitalIds.join(','),
  });
}

export function searchHospitals(params) {
  return fetchApi('/hospitals', params);
}

export function getHospital(id) {
  return fetchApi(`/hospitals/${id}`);
}

export function getProcedureStats(id, state) {
  return fetchApi(`/stats/procedure/${id}`, { state });
}
