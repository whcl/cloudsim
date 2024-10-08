from cloudsim.entities.entity import Entity

class Cloudlet(Entity):
    def __init__(self, length, pes_number, file_size, output_size):
        super().__init__()
        self.cloudlet_id = super().getId()  # Получаем уникальный идентификатор для Cloudlet
        self.length = length  # Длина задания (объем вычислений)
        self.pes_number = pes_number  # Количество процессорных элементов (PE) для выполнения задания
        self.file_size = file_size  # Размер входных данных
        self.output_size = output_size  # Размер выходных данных
        self.vm = None  # Виртуальная машина, на которой будет выполняться Cloudlet
        self.status = "Created"  # Статус задания (по умолчанию создано)
        self.finish_time = None  # Время завершения задания (изначально не задано)

    def set_vm(self, vm):
        # Устанавливаем виртуальную машину (VM) для выполнения данного Cloudlet
        self.vm = vm

    def get_vm(self):
        # Возвращаем виртуальную машину, на которой выполняется Cloudlet
        return self.vm

    def get_status(self):
        # Возвращаем текущий статус задания
        return self.status

    def get_finish_time(self):
        # Возвращаем время завершения задания
        return self.finish_time
