# TODOs
1. Build a frontend for the organizations. Could be a simple button + form.  Only one organization for now.
   - [ ] Include invites in the members table, as “pending members”
   - [ ] Add a button next to the table to send a new invite.
2. Build the frontend for the invitations:
   - [x] Frontend to accept/reject the invite
TODO: Consider how better to rewrite userMemberShip, the reason is 'enabled'

# Backend notes
1) Ought to create seperete serializer file for every applicaiton? To split message details and output data.

### Django migrations
1) Why should we keep migrations in the codebase if you constancy make new one? And we have models as base.
https://docs.djangoproject.com/en/6.1/topics/migrations/#:~:text=migrations%20as%20a%20version%20control%20system%20for%20your%20database%20schema
https://github.com/iMakedonsky/pulsePM/pull/3#discussion_r4276559810

### Project architectural pattern

# Frontend notes

@src/routes @src/router.tsx @src/routeTree.gen.ts 
Would you run thougth route files and then elaborate schematically how router works (how it bound route files.)

Prompt:
@src/components/UI/InvitationForm.tsx  
Допиши компонент.
   Компонент приймає параметри: organizationId, isVisible, onClose (as arrow func).
isVisible відповідає за відображання попап вікна;
onClose ламбда функція що дозволяю закрити вікно при натисканні на "X", або після  успішного відправлення фетч реквесту POST.
Реквест на створення запрошення:
 