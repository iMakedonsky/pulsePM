import { request } from '#/lib/apiClient.ts';

export interface getOrganizationTypes {
  owner_name: string;
  owner: number;
  name: string;
  description?: string;
}

export interface getWorkspaceTypes {
  id: number;
  name: string;
  space_code: string;
}

export interface getInvitationTypes {
  org_invite: number;
  accepted: boolean | null;
  email: string;
  expired_at: string;
  org_name: string;
}

export interface getInvitationListItemTypes {
  id: string;
  org_invite: number;
  accepted: boolean | null;
  email: string;
  sender_name: string;
  text_message: string;
  created_at: string;
  expired_at: string;
}

export interface getInvitationResponseTypes {
  accepted: boolean;
  member?: {
    user: {
      id: number;
      first_name: string;
      last_name: string;
      email: string;
    };
    id: number;
    organization: number;
    role: string;
  };
}

export const getOrganizationData = (id: number) => request<getOrganizationTypes>(`/organization/${id}`);
export const getListWorkspaces = (id: number) => request<getWorkspaceTypes[]>(`/organization/${id}/workspaces`);
export const getListInvitations = (id: number) => request<getInvitationListItemTypes[]>(`/organization/${id}/invitations`);
export const createInvitation = (orgId: number, email: string, textMessage: string) =>
  request<getInvitationTypes>(`/organization/${orgId}/invitation/create`, {
    method: 'POST',
    body: JSON.stringify({ email, text_message: textMessage }),
  });
export const getInvitation = (token: string) => request<getInvitationTypes>(`/invitation/${token}`);
export const acceptInvitation = (token: string, accepted: boolean) =>
  request<getInvitationResponseTypes>(`/invitation/${token}/accept`, {
    method: 'PATCH',
    body: JSON.stringify({ accepted }),
  });
