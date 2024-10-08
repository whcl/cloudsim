import uuid

class Entity:
    def __init__(self):
        self.id = self.generate_id()  # Генерируем уникальный идентификатор для сущности
        self.name = self.id  # Имя сущности по умолчанию совпадает с её ID

    def setName(self, name):
        # Устанавливаем имя для сущности
        self.name = name

    def getId(self):
        # Возвращаем уникальный идентификатор сущности
        return self.id

    def generate_id(self):
        # Генерируем уникальный ID с помощью библиотеки uuid
        return str(uuid.uuid4())