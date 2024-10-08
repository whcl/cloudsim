from cloudsim.entities.entity import Entity

class Vm(Entity):
    def __init__(self, broker_id, mips, pes_number, ram, bw, size, vmm):
        super().__init__()  # Инициализация базового класса
        self.vmid = self.getId()  # Получаем уникальный идентификатор виртуальной машины (VM)
        self.broker_id = broker_id  # Идентификатор брокера, управляющего этой VM
        self.mips = mips  # Рейтинг MIPS (Million Instructions Per Second) для виртуальной машины
        self.pes_number = pes_number  # Количество процессорных элементов (PE), используемых виртуальной машиной
        self.ram = ram  # Объем оперативной памяти, выделенной для VM
        self.bw = bw  # Пропускная способность виртуальной машины
        self.size = size  # Объем хранилища, выделенного для VM
        self.vmm = vmm  # Виртуальная машина мониторинга (VMM), используемая для управления этой VM

    def get_id(self):
        # Возвращаем уникальный идентификатор виртуальной машины
        return self.vmid

    def get_details(self):
        # Выводим подробную информацию о виртуальной машине
        print(f"ID VM: {self.vmid}\nMIPS: {self.mips}\nPEs: {self.pes_number}\nRAM: {self.ram}\nBW: {self.bw}\nSize: {self.size}\nVMM: {self.vmm}\n")