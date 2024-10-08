from cloudsim.entities.entity import Entity
import pandas as pd

class CloudletScheduler(Entity):
    def __init__(self, env, datacenter):
        super().__init__()
        self.env = env  # Симуляционное окружение.
        self.vm_list = datacenter.vm_list  # Список виртуальных машин (VM) в датацентре.
        self.free_vms = [vm for vm in self.vm_list]  # Изначально все виртуальные машины свободны.
        self.running_vms = []  # Список виртуальных машин, на которых выполняются задачи.
        self.clock_time = 0  # Внутренний таймер планировщика.
        self.total_execution_time = 0  # Общее время выполнения всех задач.
        # Хранение максимальной загрузки ресурсов каждой виртуальной машины (PEs, RAM, Storage).
        self.max_utilization = {vm.get_id(): [0, 0, 0] for vm in self.vm_list}

    def schedule_cloudlets(self, cloudlets):
        # Метод планирования задач, пока не реализован.
        pass

    def schedule_cloudlet(self, cloudlet):
        # Метод планирования отдельной задачи (cloudlet).
        while True:
            # Поиск первой свободной виртуальной машины, у которой достаточно ресурсов для выполнения задачи.
            selected_vm = next((vm for vm in self.free_vms if self.has_enough_resources(vm, cloudlet)), None)
            if selected_vm:
                # Если найдена подходящая VM:
                self.free_vms.remove(selected_vm)  # Удаление VM из списка свободных.
                cloudlet.set_vm(selected_vm)  # Назначение задачи на выбранную VM.
                self.running_vms.append(selected_vm)  # Добавление VM в список занятых.
                # Обновление максимальной загрузки для данной VM.
                self.max_utilization[selected_vm.get_id()] = max(self.max_utilization[selected_vm.get_id()],
                                                                 self.get_utilization(selected_vm, cloudlet))
                yield self.env.process(self.execute_cloudlet(cloudlet))
                # Запуск выполнения задачи.
                break
            else:
                # Если нет доступных ресурсов, ждем 1 единицу времени.
                yield self.env.timeout(1)

    def has_enough_resources(self, vm, cloudlet):
        # Проверка, достаточно ли ресурсов на VM для выполнения задачи.
        return vm.pes_number >= cloudlet.pes_number and vm.ram >= cloudlet.file_size and vm.size >= cloudlet.output_size

    def print_summary(self):
        # Вывод информации о времени выполнения и загрузке ресурсов.
        print(f"\nTotal Execution Time: {self.total_execution_time}")
        for vm_id, utilization in self.max_utilization.items():
            print(
                f"\nVM {vm_id} utilization:\n {utilization[0] * 100}% PEs\n, {utilization[1] * 100}% RAM\n, {utilization[2] * 100}% Storage"
            )
            # Процент использования процессорных единиц (PEs), оперативной памяти (RAM) и хранилища (Storage).

    def execute_cloudlet(self, cloudlet):
        # Выполнение задачи (cloudlet) на назначенной VM.
        print(f"Cloudlet {cloudlet.cloudlet_id} starts execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}")
        start_time = self.env.now  # Время начала выполнения задачи.
        yield self.env.timeout(
            cloudlet.length)  # Ожидание выполнения задачи в течение ее длины (длительность выполнения).
        end_time = self.env.now  # Время завершения выполнения.
        print(
            f"Cloudlet {cloudlet.cloudlet_id} completes execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}")
        execution_time = end_time - start_time  # Время выполнения задачи.
        self.total_execution_time += execution_time  # Обновление общего времени выполнения.

        # Подсчет времени ожидания и времени выполнения задачи.
        wait_time = start_time
        turnaround_time = wait_time + execution_time
        print(f"Cloudlet {cloudlet.cloudlet_id} - Waiting Time: {wait_time}, Turnaround Time: {turnaround_time}")

        # После завершения выполнения задачи, VM возвращается в список свободных.
        self.free_vms.append(cloudlet.get_vm())
        self.running_vms.remove(cloudlet.get_vm())
        self.print_summary()  # Печать сводки после выполнения задачи.

    def get_utilization(self, vm, cloudlet):
        # Получение процента загрузки ресурсов VM для конкретной задачи.
        return [cloudlet.pes_number / vm.pes_number, cloudlet.file_size / vm.ram, cloudlet.output_size / vm.size]

    def get_clock_time(self):
        # Получение текущего времени симуляции.
        return self.env.now
