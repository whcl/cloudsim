from cloudsim.entities.entity import Entity


class Broker(Entity):
    def __init__(self, datacenter):
        super().__init__()
        self.broker_id = super().getId()  # Получаем уникальный ID брокера, используя метод родительского класса
        self.datacenter = datacenter  # Связываем брокера с центром обработки данных
        self.host_list = datacenter.get_host_list()  # Получаем список хостов из центра обработки данных

    def assign_vm_to_host(self, vm):
        # Проверяем, есть ли хосты с достаточными ресурсами для размещения новой виртуальной машины (VM)
        available_hosts = [host for host in self.host_list if host.has_enough_resources(vm)]

        if not available_hosts:
            raise ValueError("Нет доступных хостов с достаточными ресурсами для размещения VM.")

        # Находим хост с наибольшим количеством доступных ресурсов
        selected_host = max(self.host_list, key=lambda host: host.available_resources())

        # Назначаем виртуальную машину на выбранный хост
        selected_host.assign_vm(vm)