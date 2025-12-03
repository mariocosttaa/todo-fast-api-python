class Paginator:
    def __init__(self, items: list, page: int, page_size: int):
        self.items = items
        self.page = page
        self.page_size = page_size

    @property
    def total_items(self):
        return len(self.items)

    @property
    def total_pages(self):
        return (self.total_items + self.page_size - 1) // self.page_size

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1

    @property
    def iter_pages(self):
        return range(1, self.total_pages + 1)

    @property
    def items_on_page(self):
        start = (self.page - 1) * self.page_size
        end = self.page * self.page_size
        return self.items[start:end]

    def prev(self):
        return self.__class__(self.items, self.prev_num, self.page_size)

    def next(self):
        return self.__class__(self.items, self.next_num, self.page_size)


def paginate(items: list, page: int, page_size: int):
    paginator = Paginator(items, page, page_size)
    return paginator.items_on_page, paginator
