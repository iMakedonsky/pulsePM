# TODOs
1. Build a frontend for the organizations. Could be a simple button + form.  Only one organization for now.
2. Build the frontend for the invitations:
   + Frontend to accept/reject the invite
   + Include invites in the members table, as “pending members”
   + Add a button next to the table to send a new invite.

# Backend notes
1) Ought to create seperete serializer file for every applicaiton? To split message details and output data.

### Django migrations
1) Why should we keep migrations in the codebase if you constancy make new one? And we have models as base.
https://docs.djangoproject.com/en/6.1/topics/migrations/#:~:text=migrations%20as%20a%20version%20control%20system%20for%20your%20database%20schema
https://github.com/iMakedonsky/pulsePM/pull/3#discussion_r4276559810

### Project architectural pattern
1) Is it ok? If I splitted large organization api endpoints into few py files, like workspace api, workitems? 
2) Is it ok? How I set aside api files, which represent organization entities models?
3) Should I have created a separerte application dirs for each entity?

# Frontend notes
TODO: Consider how better to rewrite userMemberShip, the reason is 'enabled'
