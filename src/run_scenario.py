from os import unlink
from os.path import exists
from json import load
from typing import Callable


from domain.main.Market import Market

if __name__ == '__main__':
    file_path = "../States/scenario3.json"
    if exists('workshop.db'):
        choice = input("A db file exists. "
                       "I'll delete it an create a new one. "
                       "You'll lose data. Proceed? [Yes/no]").strip().lower()
        if choice == "no":
            print("understandable, have a great day.")
            exit(0)
        elif choice != "yes":
            print("I only understand 'yes' and 'no'. To be sure, I took this as a 'no'. Goodbye!")
            exit(0)
        unlink('workshop.db')
    market = Market.Market()
    session = market.enter()

    with open(file_path, "r") as file:
        scenario = load(file)

    actions = scenario["init"]

    if not all("tag" in action for action in actions):
        print("all should have tag")
        exit(1)

    not_ok = [x for x in actions if not hasattr(session, x["tag"])]
    if not_ok:
        print(f"unknown tags: {not_ok}")
        exit(1)

    action: dict
    for action in actions:
        print(action)
        tag = action.pop('tag')
        method: Callable = getattr(session, tag)
        method(**action)

    print("all done!")
    exit(0)
