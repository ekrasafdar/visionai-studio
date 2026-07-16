const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = { ...(options.headers as Record<string, string>) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData) && options.body) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  register: (email: string, password: string, full_name?: string) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ email, password, full_name }) }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw new Error("Invalid email or password");
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data;
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  me: () => request("/auth/me"),

  predict: (file: File, modelName: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("model_name", modelName);
    return request("/predict", { method: "POST", body: form });
  },

  history: (limit = 50) => request(`/history?limit=${limit}`),

  dashboard: () => request("/dashboard"),

  models: () => request("/models"),

  retrain: (model_name: string, epochs: number, batch_size: number, learning_rate: number) =>
    request("/retrain", { method: "POST", body: JSON.stringify({ model_name, epochs, batch_size, learning_rate }) }),

  trainingStatus: (id: string) => request(`/retrain/${id}`),

  profile: () => request("/profile"),

  updateProfile: (full_name?: string, avatar_url?: string) =>
    request("/profile", { method: "PUT", body: JSON.stringify({ full_name, avatar_url }) }),

  fileUrl: (path: string) => `${API_URL}/${path.replace(/^\.?\/?/, "")}`,
};
