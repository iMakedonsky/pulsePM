export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface MemberShip {
  id: number;
  organization: { id: number; name: string };
  role: string;
  position: string;
  last_activity: string;
}

export interface OrganizationTypes {
  owner: number;
  name: string;
  description?: string;
}

export interface WorkspaceTypes {
  id: number;
  name: string;
  space_code: string;
  created_by: number;
}

export interface MembeList {
  id: number;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// TODO: Consider about Cashe usage. Is that necessary to add all of that?
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

export const signUp = (email: string, password: string) =>
  request<AuthUser>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

export const login = (email: string, password: string) =>
  request<AuthUser>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

export const logout = () => request<void>('/auth/logout', { method: 'POST' });

export const getCurrentUser = () => request<AuthUser>('/user/profile');
export const getUserMemberShip = () => request<MemberShip[]>('/user/memberships');
export const getOrganizationData = (id: number) => request<OrganizationTypes>(`/organization/${id}`);
export const getListWorkspaces = (id: number) => request<WorkspaceTypes[]>(`/organization/${id}/workspaces`);
