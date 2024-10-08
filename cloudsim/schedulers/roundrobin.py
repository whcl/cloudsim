from cloudsim.schedulers.cloudlet_scheduler import CloudletScheduler
from simpy.events import AnyOf

class CloudletSchedulerRoundRobin(CloudletScheduler):
    def __init__(self, env, datacenter, time_slice=2):
        super().__init__(env, datacenter)
        # Инициализация планировщика с окружением и датацентром, передается временной интервал (time_slice) для задач.
        self.time_slice = time_slice  # Время, в течение которого задача может выполняться на одном цикле (квант времени).
        self.total_execution_time = 0  # Общее время выполнения всех задач.
        self.total_turn_around_time = 0  # Время завершения выполнения всех задач.
        self.max_utilization = {}  # Хранение максимальной загрузки ресурсов для каждой виртуальной машины (VM).

    def schedule_cloudlets(self, cloudlets):
        remaining_cloudlets = list(cloudlets)  # Создание копии списка задач для обработки.
        while remaining_cloudlets:
            batch = remaining_cloudlets[:len(self.vm_list)]
            # Выбор подмножества задач по количеству доступных виртуальных машин (VM).
            remaining_cloudlets = remaining_cloudlets[len(batch):]
            # Удаление выбранных задач из оставшихся.

            completion_events = [self.env.process(self.schedule_cloudlet(cloudlet)) for cloudlet in batch]
            # Запуск выполнения каждой задачи в отдельном процессе симуляции.
            yield AnyOf(self.env, completion_events)
            # Ожидание завершения любого процесса.


    def print_summary(self):
        # Вывод суммарных данных о времени выполнения и загрузке каждой виртуальной машины.
        print(f"\nTotal Execution Time: {self.total_execution_time}")
        for vm_id, utilization in self.max_utilization.items():
            print(
                f"\nVM {vm_id} utilization:\n {utilization[0] * 100}% PEs\n, {utilization[1] * 100}% RAM\n, {utilization[2] * 100}% Storage"
            )
            # Вывод процента использования процессорных единиц (PEs), оперативной памяти (RAM) и хранилища для каждой VM.

    def schedule_cloudlet(self, cloudlet):
        # Функция планирования и выполнения одной задачи (cloudlet).
        while cloudlet.length > 0:
            # Пока длина задачи (длительность выполнения) больше 0:
            for selected_vm in self.free_vms[:]:
                # Поиск свободной виртуальной машины.
                if self.has_enough_resources(selected_vm, cloudlet):
                    # Проверка, достаточно ли ресурсов на данной VM для выполнения задачи.
                    self.free_vms.remove(selected_vm)
                    # Удаление VM из списка свободных.
                    cloudlet.set_vm(selected_vm)
                    # Назначение задачи на выбранную VM.
                    self.running_vms.append(selected_vm)
                    # Добавление VM в список выполняющих задачи.
                    self.max_utilization[selected_vm.get_id()] = max(
                        self.max_utilization.get(selected_vm.get_id(), [0, 0, 0]),
                        # Обновление максимальной загрузки ресурсов на этой VM.
                        self.get_utilization(selected_vm, cloudlet)
                    )

                    print(
                        f"Cloudlet {cloudlet.cloudlet_id} starts execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}"
                    )
                    # Вывод информации о начале выполнения задачи.

                    execution_time = min(self.time_slice, cloudlet.length)
                    # Определение времени выполнения за один цикл (ограничено `time_slice`).
                    yield self.env.timeout(execution_time)
                    # Ожидание завершения выполнения за выделенное время.
                    cloudlet.length -= execution_time
                    # Уменьшение оставшегося времени задачи.

                    print(
                        f"Cloudlet {cloudlet.cloudlet_id} completes execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}"
                    )
                    # Вывод информации о завершении выполнения задачи.

                    self.running_vms.remove(selected_vm)
                    # Удаление VM из списка выполняющих задачи.
                    self.free_vms.append(selected_vm)
                    # Возвращение VM в список свободных.

                    self.total_execution_time += execution_time
                    # Обновление общего времени выполнения.
                    #self.print_summary()
                    # Печать сводки.
                    break
            else:
                print(f"No available VM for Cloudlet {cloudlet.cloudlet_id} at {self.env.now}, waiting...")
                yield self.env.timeout(1)
                # Если нет доступных ресурсов, ждем 1 единицу времени.
