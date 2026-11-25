import * as SecureStore from 'expo-secure-store';

export const API_URL = (process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'checkin_api_token';

export const getToken = () => SecureStore.getItemAsync(TOKEN_KEY);
export const saveToken = (token) => SecureStore.setItemAsync(TOKEN_KEY, token);
export const clearToken = () => SecureStore.deleteItemAsync(TOKEN_KEY);

async function request(method, path, body) {
  const token = await getToken();
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(errorText(data) || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

function errorText(data) {
  if (!data || !data.detail) return null;
  if (typeof data.detail === 'string') return data.detail;
  // FastAPI validation errors: [{loc, msg}, ...]
  return data.detail.map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg.replace(/^Value error, /, '')}`).join('\n');
}

export const api = {
  register: (user) => request('POST', '/users', user),
  me: () => request('GET', '/me'),
  updateMe: (changes) => request('PATCH', '/me', changes),
  deleteMe: () => request('DELETE', '/me'),
  contacts: () => request('GET', '/me/contacts'),
  addContact: (c) => request('POST', '/me/contacts', c),
  updateContact: (id, c) => request('PATCH', `/me/contacts/${id}`, c),
  deleteContact: (id) => request('DELETE', `/me/contacts/${id}`),
  checkins: (limit = 30) => request('GET', `/me/checkins?limit=${limit}`),
  checkIn: (status, note) => request('POST', '/me/checkins', { status, note }),
};

export function deviceTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
}

export function formatWhen(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString([], { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
