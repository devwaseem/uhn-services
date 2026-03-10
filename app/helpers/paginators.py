from math import ceil


class Page:
    def __init__(self, page: int | None = None) -> None:
        self.page = page

    @property
    def is_page(self) -> bool:
        return self.page is not None

    @property
    def value(self) -> str:
        return str(self.page) if self.page else "..."

    def __str__(self) -> str:
        return self.value


class SimplePaginator:
    def __init__(
        self,
        num_items: int,
        items_per_page: int,
        current_page: int = 1,
        delta: int = 2,
    ) -> None:
        self.delta = delta
        self.num_items = num_items
        self.items_per_page = items_per_page
        self.num_pages = ceil(num_items / items_per_page)
        self.current_page = current_page

    @property
    def items_from_in_current_page(self) -> int:
        return self.items_per_page * (self.current_page - 1) + 1

    @property
    def items_to_in_current_page(self) -> int:
        return min(self.items_per_page * self.current_page, self.num_items)

    @property
    def has_next(self) -> bool:
        return self.current_page < self.num_pages

    @property
    def next_page(self) -> int | None:
        return self.current_page + 1 if self.has_next else None

    @property
    def has_previous(self) -> bool:
        return self.current_page > 1

    @property
    def previous_page(self) -> int | None:
        return self.current_page - 1 if self.has_previous else None

    @property
    def current_page_str(self) -> str:
        return str(self.current_page)

    @property
    def pages(self) -> list[Page]:
        pages: list[Page] = []
        left = self.current_page - self.delta
        right = self.current_page + self.delta
        pages_range = [
            i
            for i in range(1, self.num_pages + 1)
            if i == 1 or i == self.num_pages or (left <= i <= right)
        ]
        prev_page = None
        for page in pages_range:
            if prev_page and (prev_page + 1) != page:
                pages.append(Page())
            page_obj = Page(page=page)
            pages.append(page_obj)
            prev_page = page

        return pages
