from cloudsim.entities.entity import Entity
from cloudsim.entities.broker import Broker


class DatacenterCharacteristics:
    def __init__(self, arch, os, vmm, host_list, time_zone, cost, cost_per_mem, cost_per_storage, cost_per_bw):
        # Характеристики датацентра: архитектура, ОС, VMM (виртуальный монитор), список хостов, часовой пояс, затраты
        self.arch = arch  # Архитектура датацентра
        self.os = os  # Операционная система
        self.vmm = vmm  # Виртуальная машина-монитор (VMM)
        self.host_list = host_list  # Список хостов (серверов)
        self.time_zone = time_zone  # Часовой пояс
        self.cost = cost  # Стоимость использования датацентра
        self.cost_per_mem = cost_per_mem  # Стоимость за использование памяти
        self.cost_per_storage = cost_per_storage  # Стоимость за использование хранилища
        self.cost_per_bw = cost_per_bw  # Стоимость за использование пропускной способности
        self.number_of_pes = 0  # Общее количество процессорных элементов (PE)
        self.set_number_of_pes()  # Устанавливаем количество PE
        self.id = 0  # Идентификатор датацентра

    def set_number_of_pes(self):
        # Подсчет общего числа процессорных элементов (PE) по всем хостам
        for host in self.host_list:
            self.number_of_pes += len(host.pe_list)

    def set_id(self, id):
        # Устанавливаем идентификатор датацентра
        self.id = id


class Datacenter(Entity):
    def __init__(self, name, characteristics, vm_allocation_policy, storage_list, scheduling_interval):
        super().__init__()
        self.setName(name)  # Устанавливаем имя датацентра

        self.characteristics = characteristics  # Характеристики датацентра
        self.vm_allocation_policy = vm_allocation_policy  # Политика выделения виртуальных машин
        self.last_process_time = 0.0  # Последнее время обработки
        self.storage_list = storage_list  # Список хранилищ
        self.vm_list = []  # Список виртуальных машин (VM)
        self.scheduling_interval = scheduling_interval  # Интервал планирования задач
        self.broker = Broker(self)  # Создаем брокера для управления распределением VM

        # Привязываем хосты к датацентру
        for host in self.characteristics.host_list:
            host.set_datacenter(self)

        # Проверка наличия PE в датацентре
        if self.characteristics.number_of_pes == 0 and len(self.characteristics.host_list) != 0:
            raise Exception(
                f"{super().getName()}: Ошибка - в данном датацентре нет PE, поэтому он не может обрабатывать Cloudlet'ы.")

        # Если есть PE, выводим сообщение о создании межоблачной сети
        if self.characteristics.number_of_pes != 0 and len(self.characteristics.host_list) != 0:
            print(f"{name}: создана межоблачная топология сети...")

        self.characteristics.set_id(super().getId())  # Устанавливаем ID для датацентра

    def set_vms(self, vm_list):
        # Назначаем список виртуальных машин (VM) для датацентра
        self.vm_list = vm_list
        for vm in vm_list:
            self.broker.assign_vm_to_host(vm)  # Передаем VM брокеру для распределения по хостам

    def get_host_list(self):
        # Возвращаем список хостов датацентра
        return self.characteristics.host_list

    def get_broker_id(self):
        # Возвращаем идентификатор брокера
        return self.broker.broker_id

    def get_vm_list(self):
        # Возвращаем список виртуальных машин (VM)
        return self.vm_list

    def get_total_cost(self):
        # Вычисляем и выводим общие затраты на использование датацентра
        print("Стоимость датацентра: ", self.characteristics.cost)
        memory_cost = self.characteristics.cost_per_mem * sum(host.ram for host in self.characteristics.host_list)
        print("Стоимость памяти: ", memory_cost)
        storage_cost = self.characteristics.cost_per_storage * sum(
            host.storage for host in self.characteristics.host_list)
        print("Стоимость хранилища: ", storage_cost)
        bw_cost = self.characteristics.cost_per_bw * sum(host.bw for host in self.characteristics.host_list)
        print("Стоимость пропускной способности: ", bw_cost)
        total_cost = self.characteristics.cost + memory_cost + storage_cost + bw_cost
        print("Общая стоимость: ", total_cost)
        print()

    def get_details(self):
        # Выводим подробную информацию о датацентре: имя, количество хостов, количество VM
        print(
            f"Имя датацентра: {self.name}\nКоличество хостов: {len(self.get_host_list())}\nКоличество VM: {len(self.get_vm_list())}\n")
        for host in self.get_host_list():
            host.get_details()  # Выводим подробную информацию для каждого хоста