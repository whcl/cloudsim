from cloudsim.entities.entity import Entity

class Pe(Entity):
    def __init__(self, mips_rating):
        super().__init__()  # Инициализация базового класса
        self.pe_id = super().getId()  # Получаем уникальный идентификатор процессорного элемента (PE)
        self.mips_rating = mips_rating  # Устанавливаем рейтинг MIPS (Million Instructions Per Second) для PE