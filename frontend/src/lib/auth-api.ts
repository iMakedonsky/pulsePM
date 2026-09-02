export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export const currentUserQueryKey = ['auth', 'me'] as const;

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const currentUserQueryKey = ['auth', 'me'] as const;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new ApiError(response.status, body?.detail ?? 'Something went wrong.');
  }

  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const getCurrentUser = () => request<AuthUser>('/auth/me');

export const signUp = (email: string, password: string) =>
  request<AuthUser>('/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

export const login = (email: string, password: string) =>
  request<AuthUser>('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

export const logout = () => request<void>('/logout', { method: 'POST' });
