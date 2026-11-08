import { request } from '#/lib/apiClient.ts';

export interface getAuthUserTypes {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface getMemberShipTypes {
  id: number;
  organization: { id: number; name: string };
  role: string;
  position: string;
  last_activity: string;
}

// TODO: Consider about Cashe usage. Is that necessary to add all of that?
export const currentUserQueryKey = ['auth', 'me'] as const;

export const signUp = (email: string, password: string, token?: string | null) =>
  request<getAuthUserTypes>('/auth/register', {
    method: 'POST',
    // TODO: How do I hand token better? (cache / cookie / payload)
    body: JSON.stringify({ email, password, token }),
  });

export const login = (email: string, password: string) =>
  request<getAuthUserTypes>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

export const logout = () => request<void>('/auth/logout', { method: 'POST' });
export const getCurrentUser = () => request<getAuthUserTypes>('/user/profile');
export const getUserMemberShip = () => request<getMemberShipTypes[]>('/user/memberships');
