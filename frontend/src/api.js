// Backend REST API istemcisi. JWT anahtarlarını saklar, süresi dolan erişim
// anahtarını otomatik yeniler ve hataları anlamlı mesajlarla fırlatır.

const API_BASE = import.meta.env.VITE_API_URL || "/api";
const TOKEN_KEY = "famsecur.tokens";

export class ApiError extends Error {
  constructor(message, status, errors = {}) {
    super(message);
    this.status = status;
    this.errors = errors;
  }
}

export const tokens = {
  get() {
    try {
      return JSON.parse(localStorage.getItem(TOKEN_KEY)) || null;
    } catch {
      return null;
    }
  },
  set(value) {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(value));
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
  },
};

let onSessionExpired = () => {};
export function setSessionExpiredHandler(handler) {
  onSessionExpired = handler;
}

let refreshing = null;
async function refreshAccessToken() {
  const current = tokens.get();
  if (!current?.refresh) return false;
  refreshing ??= fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: current.refresh }),
  })
    .then(async (res) => {
      if (!res.ok) return false;
      const data = await res.json();
      tokens.set({ access: data.access, refresh: data.refresh || current.refresh });
      return true;
    })
    .catch(() => false)
    .finally(() => {
      refreshing = null;
    });
  return refreshing;
}

async function request(method, path, body, { auth = true, retry = true } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const access = tokens.get()?.access;
  if (auth && access) headers.Authorization = `Bearer ${access}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Sunucuya ulaşılamadı. İnternet bağlantınızı veya API sunucusunu kontrol edin.", 0);
  }

  if (res.status === 401 && auth && access && retry) {
    if (await refreshAccessToken()) return request(method, path, body, { auth, retry: false });
    tokens.clear();
    onSessionExpired();
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(data?.detail || `Beklenmeyen hata (HTTP ${res.status})`, res.status, data?.errors || {});
  }
  return data;
}

export const api = {
  get: (path, opts) => request("GET", path, undefined, opts),
  post: (path, body, opts) => request("POST", path, body ?? {}, opts),
  put: (path, body, opts) => request("PUT", path, body, opts),
  patch: (path, body, opts) => request("PATCH", path, body, opts),
  delete: (path, opts) => request("DELETE", path, undefined, opts),
};

// Sayfalanmış liste yanıtlarını ({results: [...]}) ve düz listeleri aynı biçime getirir.
export const asList = (data) => (Array.isArray(data) ? data : data?.results ?? []);

export function fieldErrors(error) {
  if (!(error instanceof ApiError)) return {};
  return Object.fromEntries(
    Object.entries(error.errors || {}).map(([key, value]) => [key, Array.isArray(value) ? value.join(" ") : String(value)])
  );
}
