from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Logger import report
from src.domain.main.Utils.Response import Response




class OwnersApproval(Base):
    __tablename__ = 'owner_approvals'
    __table_args__ = {'extend_existing': True}
    approval_id = Column("approval_id", Integer, primary_key=True)
    store_name = Column("store_name", String, default='')
    person_to_approve = Column("person_to_approve", String, default='')
    starter = Column("starter", String, default='')
    to_approve_str = Column("purchase_history_str", String, default='')

    def __init__(self, approval_id, l: list, sender:str, store_name="", person_to_approve=""):
        self.approval_id = approval_id
        self.store_name = store_name
        self.person_to_approve = person_to_approve
        self.to_approve = {}
        self.starter = sender
        self.to_approve_str = ''
        for person in l:
            if person == sender:
                self.to_approve[sender] = True
                self.to_approve_str += f'{person}:1,'
            else:
                self.to_approve[person] = False
                self.to_approve_str += f'{person}:0,'

    def remove_owner(self, person: str):
        self.to_approve.pop(person)
        names_list = self.to_approve_str.split(',')
        updated_list = [item for item in names_list if not item.startswith(person)]
        self.to_approve_str = ','.join(updated_list)
        DAL.update(self)

    def add_owner(self, person: str):
        self.to_approve[person] = False
        self.to_approve_str += f'{person}:0'

    def approve(self, person: str) -> Response:
        self.to_approve[person] = True
        names_list = self.to_approve_str.split(',')
        updated_list = []
        for item in names_list:
            if len(item) > 2:
                name, value = item.split(':')
                if name == person:
                    item = f"{name}:1"
                updated_list.append(item)
        self.to_approve_str = ','.join(updated_list)

        res = self.is_approved()
        if not res.result:
            return res
        return report(f"{person} approved bid", True)

    def is_approved(self) -> Response[bool]:
        for p in self.to_approve:
            if not self.to_approve[p]:
                return report(f"is_approved {p} not approved yet", False)

        return report("approved", True)

    def restore(self):
        for p in self.to_approve:
            self.to_approve[p] = False

    def left_to_approve(self) -> list[str]:
        l = []
        for p in self.to_approve:
            if not self.to_approve[p]:
                l.append(p)
        return l

    @staticmethod
    def create_instance_from_db_query(r):
        approval_id, store_name, person_to_approve, starter, to_approve_str = \
            r.approval_id, r.store_name, r.person_to_approve, r.starter, r.to_approve_str

        names_list = to_approve_str.split(',')
        parsed_dict = {}
        for item in names_list:
            if len(item) > 2:
                name, value = item.split(':')
                parsed_dict[name] = bool(int(value))

        approval = OwnersApproval(approval_id, [], starter, store_name, person_to_approve)
        approval.to_approve = parsed_dict
        approval.to_approve_str = to_approve_str
        return approval

    @staticmethod
    def load_all_approvals_for_owners(store_name):
        out = ConcurrentDictionary()
        for a in DAL.load_all_by(OwnersApproval, lambda r: r.store_name == store_name, OwnersApproval.create_instance_from_db_query):
            out.insert(a.person_to_approve, a)
        return out

    @staticmethod
    def add_record(approval):
        DAL.add(approval)

    @staticmethod
    def delete_record(approval_id):
        DAL.delete(OwnersApproval, lambda r: r.approval_id == approval_id)