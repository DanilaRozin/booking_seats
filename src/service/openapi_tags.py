"""Модуль предназначен для автоматического добавления описаний к тэгам спецификации API."""


class OpenAPITags:
    """Класс для автоматического сбора наименования тегов и их описаний.

    Поле "tag_list" необходимо использовать в настроках приложения для передачи
    описаний тэгов, переданных через метод add_tag().
    """

    tag_list: list[dict] = []

    def add_tag(self, name: str, description: str | None = None) -> str:
        """Добавление тега в общий список.

        Note:
            Метод необходимо использовать при добавлении тэгов роутеру или
            конкретному эндпоинту вместо строки с названием тэга.

        Returns:
            Наименование тэга, указанного в аргументе метода.

        """
        for tag in self.tag_list:
            if name in tag.values():
                return name
        self.tag_list.append({'name': name, 'description': description})
        return name
