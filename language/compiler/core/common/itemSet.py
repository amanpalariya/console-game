from compiler.core.common.item import Item


class ItemSet:
    def __init__(self, *items: [Item]):
        self.__items = set({*items})

    @staticmethod
    def union(itemSet1, itemSet2):
        return ItemSet(*itemSet1.getItems(), *itemSet2.getItems())

    def getItems(self):
        return self.__items

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__items})"

    def __eq__(self, other):
        itemsEqual = self.getItems() == other.getItems()
        return itemsEqual

    def __hash__(self):
        return hash(tuple(self.__items))
