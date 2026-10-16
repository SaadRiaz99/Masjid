"""Business rules for user accounts and roles."""

from __future__ import annotations

from ..models import User
from .errors import ValidationError
from .permissions import Actor, require


class UserService:
    """Create, read, update and delete user accounts.

    Rules enforced here:
    * only admins may create, edit or delete accounts - everyone else can
      read the list (see :mod:`business.permissions`);
    * usernames are unique (case-insensitive);
    * role and status must be valid choices.
    """

    entity = "user"

    def __init__(self, store, actor: Actor | None = None):
        self.store = store
        self.actor = actor or Actor()

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def list(self) -> list[dict]:
        require(self.actor, self.entity, "read")
        return [user.to_row() for user in self._records()]

    def get(self, user_id) -> dict:
        require(self.actor, self.entity, "read")
        return self._find(user_id).to_row()

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create(self, data: dict) -> dict:
        require(self.actor, self.entity, "create")
        user = User.from_row(data)
        self._ensure_username_free(user.username)
        user.id = self.store.next_id()
        self.store.insert(user.to_row())
        return user.to_row()

    def update(self, user_id, data: dict) -> dict:
        require(self.actor, self.entity, "update")
        existing = self._find(user_id)

        merged = {**existing.to_row(), **{k: v for k, v in data.items() if k != "id"}}
        user = User.from_row(merged)
        user.id = existing.id
        if user.username.casefold() != existing.username.casefold():
            self._ensure_username_free(user.username)

        rows = self.store.all()
        for index, row in enumerate(rows):
            if str(row.get("id")) == str(user.id):
                rows[index] = user.to_row()
        self.store.save(rows)
        return user.to_row()

    def delete(self, user_id) -> None:
        require(self.actor, self.entity, "delete")
        existing = self._find(user_id)
        self.store.save(
            [row for row in self.store.all() if str(row.get("id")) != str(existing.id)]
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _records(self) -> list[User]:
        return [User.from_row(row) for row in self.store.all()]

    def _find(self, user_id) -> User:
        for user in self._records():
            if str(user.id) == str(user_id):
                return user
        raise ValidationError(f"User with id {user_id} was not found.")

    def _ensure_username_free(self, username: str) -> None:
        wanted = username.casefold()
        if any(user.username.casefold() == wanted for user in self._records()):
            raise ValidationError(f"The username {username!r} is already taken.")
