# conversational flow

/start
"Welcome to the Tapout Bot! Enter the password:"
>Mel's mom

"That's wrong - try again.  I will ban you after ${} failed attempts."
>asdf

"Talk to the hand ✋🏻 you are banned!"


"What unit are you working on today?"
>E3

/stop
"Done - no longer notifyting you for tapouts on ${}."

# user database entry

```json
{
    user_chat_id: 123456789,
    unit: "E3",
    call: null,
}
```

# method for handling websocket messages

Every time we get a websocket message I ASSUME it is a list of unit updates.

I take the list of users from the database with their assigned unit.

I remove the users from the list if their assignedCall == the call of the unit they are working on.

const someoneGotTappedOut = unitsWithACall.filter(unit => unit.call !== null).length > 0

The remaining users have a 'status change' - either they need to be tapped or they have been cleared.

If we have any status changes... I query the server for the incident list.

if their current call is not null and their assigned call is null - they have been cleared.
> message these users and drop them from the list
