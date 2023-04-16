from dev.src.main.User.Role.Member import Member


class StoreOwner(Member):
    from dev.src.main.User.User import User
    def __init__(self, context: User, store_name: str):
        super().__init__(context)
        self.context.appointees.update({store_name: []})
        self.context.founded_stores.append(store_name)

    def __str__(self):
        return f'StoreOwner {self.context.username}'
