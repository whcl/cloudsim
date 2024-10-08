#simulate cloud load using datacenter and simpy tool
import simpy
from cloudsim.schedulers.fcfs import CloudletSchedulerFCFS
from cloudsim.schedulers.sjf import CloudletSchedulerSJF
from cloudsim.schedulers.roundrobin import CloudletSchedulerRoundRobin
from cloudsim.schedulers.PS import PSOCloudletScheduler  # Импортируем класс PSOCloudletScheduler
import pandas as pd


class CloudletExecution:
    def __init__(self, schedular, cloudlet_list, datacenter):
        self.cloudlet_list = cloudlet_list
        self.scheduler = schedular
        self.env = simpy.Environment()
        self.df_summary = []
        if self.scheduler == "FCFS":
            self.scheduler_instance = CloudletSchedulerFCFS(self.env, datacenter)
        if self.scheduler == "SJF":
            self.scheduler_instance = CloudletSchedulerSJF(self.env, datacenter)
        if self.scheduler == "RoundRobin":
            self.scheduler_instance = CloudletSchedulerRoundRobin(self.env, datacenter)
        if self.scheduler == "PS":
            self.scheduler_instance = PSOCloudletScheduler(self.env, datacenter, 10, 20)

    def execute(self):
        print(f"Using {self.scheduler} scheduler \n")
        self.env.process(self.scheduler_instance.schedule_cloudlets(self.cloudlet_list))
        self.env.run()
        #self.scheduler_instance.print_summary()

    def create_summary_dataset(self):
        # Инициализация списка для хранения данных
        data = []

        # Проход по каждой виртуальной машине и сбор данных
        for vm_id, utilization in self.scheduler_instance.max_utilization.items():
            data.append({
                "scheduler": self.scheduler,
                "total_execution_time": self.scheduler_instance.total_execution_time,
                "vm_id": vm_id,
                "PE_usage": utilization[0] * 100,  # Процент использования PEs
                "RAM_usage": utilization[1] * 100,  # Процент использования RAM
                "Storage_usage": utilization[2] * 100  # Процент использования Storage
            })

        # Создание DataFrame
        df = pd.DataFrame(data)

        # Возвращение DataFrame для дальнейшей обработки
        return df
