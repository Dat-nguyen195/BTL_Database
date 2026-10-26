let csrf;
export async function api(path, body) {
  if (!csrf) {
    const r = await fetch('/api/v1/auth/csrf');
    const data = await r.json();
    if (!r.ok) throw new Error(data.error?.message || 'Không lấy được CSRF.');
    csrf = data.data.CsrfToken;
  }
  const response = await fetch('/api/v1' + path, body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body: JSON.stringify(body)
  });
  const result = await response.json();
  if (!response.ok) {
    if (response.status === 401 || result.error?.code === 'CSRF_INVALID') csrf = undefined;
    throw new Error(`${result.error?.code}: ${result.error?.message} (requestId ${result.requestId})`);
  }
  if (result.data?.CsrfToken) csrf = result.data.CsrfToken;
  if (path === '/auth/logout') csrf = undefined;
  return result;
}
export function code(prefix) {
  return prefix + Array.from(crypto.getRandomValues(new Uint8Array(10)), n => n.toString(16).padStart(2,'0')).join('').slice(0,19).toUpperCase();
}
