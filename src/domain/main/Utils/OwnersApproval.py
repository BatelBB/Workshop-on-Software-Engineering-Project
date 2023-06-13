from domain.main.Utils.Logger import report
from domain.main.Utils.Response import Response


class OwnersApproval:
    to_approve: dict[str, bool]

    def __init__(self, l: list, sender:str):
        self.to_approve = {}
        for person in l:
            if person == sender:
                self.to_approve[sender] = True
            else:
                self.to_approve[person] = False
                # TODO: send messages to person

    def remove_owner(self, person: str):
        self.to_approve.pop(person)

    def add_owner(self, person: str):
        # TODO: send messages to person
        self.to_approve[person] = False

    def approve(self, person: str) -> Response:
        self.to_approve[person] = True
        res = self.is_approved()
        if res.result:
            return res
        return report(f"{person} approved bid", True)

    def is_approved(self) -> Response[bool]:
        for p in self.to_approve:
            if not self.to_approve[p]:
                return report(f"is_approved {p} not approved yet", False)

        return report("approved", True)