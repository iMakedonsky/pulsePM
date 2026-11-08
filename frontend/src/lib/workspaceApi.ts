import { request } from '#/lib/apiClient.ts';

export interface getWorkspaceType {
  creator_name: string;
  id: number;
  name: string;
  space_code: string;
  icon_url: string;
  description: string;
  created_by: number;
}

export interface updateWorkspacePayload {
  name: string;
  icon_url: string;
  description: string;
}

export interface getWorkItemsTypes {
  id: number;
  assigned_to: number;
  title: string;
  status: string;
  priority: string;
  created_at: string;
  due_date?: string;
  last_modified_by: string;
}

export const getWorkspace = (org_id: number, workpsace_id: number) =>
  request<getWorkspaceType>(`/organization/${org_id}/workspaces/${workpsace_id}`);
export const updateWorkspace = (org_id: number, workpsace_id: number, name?: string, description?: string, icon_url?: string) =>
  request<updateWorkspacePayload>(`/organization/${org_id}/workspaces/${workpsace_id}`, {
    method: 'PATCH',
    body: JSON.stringify({ name, description, icon_url }),
  });
export const getListWorkitems = (org_id: number, workpsace_id: number) =>
  request<getWorkItemsTypes>(`/organization/${org_id}/workspaces/${workpsace_id}/workitems`);
export const deleteWorkspace = (org_id: number, workpsace_id: number) =>
  request<getWorkspaceType>(`/organization/${org_id}/workspaces/${workpsace_id}`, {
    method: 'DELETE',
  });
