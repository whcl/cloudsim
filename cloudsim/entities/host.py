from cloudsim.entities.entity import Entity


class Host(Entity):
    def __init__(self, ram, bw, storage, pe_list):
        super().__init__()  # Инициализация базового класса
        self.host_id = super().getId()  # Получаем уникальный идентификатор хоста
        self.ram = ram  # Объем оперативной памяти хоста
        self.bw = bw  # Пропускная способность хоста
        self.storage = storage  # Объем хранилища хоста
        self.pe_list = pe_list  # Список процессорных элементов (PE)
        self.assigned_vms = []  # Список назначенных виртуальных машин (VM)

    def set_datacenter(self, datacenter):
        # Устанавливаем датацентр для хоста
        self.datacenter = datacenter

    def available_resources(self):
        # Вычисляем доступные ресурсы, вычитая использованные ресурсы из общего объема
        used_ram = sum(vm.ram for vm in self.assigned_vms)  # Используемая память
        used_bw = sum(vm.bw for vm in self.assigned_vms)  # Используемая пропускная способность
        used_storage = sum(vm.size for vm in self.assigned_vms)  # Используемое хранилище
        pes = sum(vm.pes_number for vm in self.assigned_vms)  # Используемое количество PE

        # Вычисляем доступные ресурсы
        available_ram = self.ram - used_ram
        available_bw = self.bw - used_bw
        available_storage = self.storage - used_storage
        available_pes = len(self.pe_list) - pes

        return available_ram, available_bw, available_storage, available_pes  # Возвращаем доступные ресурсы

    def has_enough_resources(self, vm):
        # Проверяем, достаточно ли ресурсов у хоста для размещения виртуальной машины (VM)
        available_ram, available_bw, available_storage, available_pes = self.available_resources()
        return (vm.ram <= available_ram) and (vm.bw <= available_bw) and (vm.size <= available_storage) and (
                    vm.pes_number <= available_pes)

    def assign_vm(self, vm):
        # Проверяем, достаточно ли ресурсов для назначения VM
        available_ram, available_bw, available_storage, available_pes = self.available_resources()

        if (vm.ram > available_ram) or (vm.bw > available_bw) or (vm.size > available_storage) or (
                vm.pes_number > available_pes):
            raise ValueError("Недостаточно доступных ресурсов для выделения VM.")

        # Назначаем VM хосту
        self.assigned_vms.append(vm)

    def get_details(self):
        # Выводим подробную информацию о хосте
        print(
            f"ID хоста: {self.host_id}\nОперативная память: {self.ram}\nПропускная способность: {self.bw}\nХранилище: {self.storage}\nКоличество PE: {len(self.pe_list)}\n")
        for vm in self.assigned_vms:
            vm.get_details()  # Выводим информацию о каждой назначенной VM