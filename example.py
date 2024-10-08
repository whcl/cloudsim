from cloudsim.entities.datacenter import Datacenter, DatacenterCharacteristics
from collections import deque
from cloudsim.entities.vm import Vm
from cloudsim.entities.host import Host
from cloudsim.entities.pe import Pe
from cloudsim.entities.cloudlet import Cloudlet
from cloudsim.simulation.cloudlet import CloudletExecution
import random
import pandas as pd


def create_datacenter(name):
    # Create a list to store the host machines
    host_list = []

    # Create PEs (Processing Elements) and add them to the list
    pe_list = [Pe(1000), Pe(1000), Pe(1000),Pe(1000)]  # Assuming MIPS value is 1000

    # Create a Host with its specifications and add it to the list
    ram = 4096  # Host memory (MB)
    storage = 1000000  # Host storage
    bw = 10000

    host_list.append(
        Host(
            ram,
            bw,
            storage,
            pe_list
        )
    )  # This is our host machine

    # Create a DatacenterCharacteristics object
    arch = "x86"
    os = "Linux"
    vmm = "Xen"
    time_zone = 10.0
    cost = 100.0
    cost_per_mem = 0.10
    cost_per_storage = 0.002
    cost_per_bw = 0.0
    storage_list = deque()  # We are not adding SAN devices for now

    characteristics = DatacenterCharacteristics(
        arch, os, vmm, host_list, time_zone, cost, cost_per_mem, cost_per_storage, cost_per_bw
    )

    # Finally, create a Datacenter object
    datacenter = Datacenter(name, characteristics, None, storage_list, 0)

    return datacenter

# Example usage:
datacenter_instance = create_datacenter("MyDatacenter")

broker_id = datacenter_instance.get_broker_id()

# Create a list to store the VMs
vmlist = []

# VM specifications
mips = 250
size = 10000  # Image size (MB)
ram = 1024  # VM memory (MB)
bw = 2000
pes_number = 1  # Number of CPUs
vmm = "Xen"  # VMM name

# Create two VMs
vm1 = Vm(broker_id, mips*2, pes_number, ram*0.8, bw, size, vmm)
vm2 = Vm(broker_id, mips*0.7, pes_number*2, ram*0.5, bw, size, vmm)
vm3 = Vm(broker_id, mips*0.5, pes_number, ram*2, bw, size, vmm)

# Add the VMs to the vmList
vmlist.extend([vm1, vm2, vm3])

# Set the VMs for the datacenter
datacenter_instance.set_vms(vmlist)

# Display details of the datacenter and calculate total cost
datacenter_instance.get_details()
datacenter_instance.get_total_cost()


# Create a list of Cloudlets
def generate_random_cloudlets(num_cloudlets):
    cloudlets = []
    for i in range(num_cloudlets):
        length = random.randint(1, 15)  # Длина облачного лета от 1 до 20
        pes_number = random.randint(1, 2)  # Количество PE от 1 до 4
        file_size = random.randint(100, 500)  # Размер файла от 50 до 200
        output_size = random.randint(30, 150)  # Размер вывода от 30 до 150

        cloudlet = Cloudlet(length=length, pes_number=pes_number,
                            file_size=file_size, output_size=output_size)
        cloudlets.append(cloudlet)

    return cloudlets

cloudlet_list = generate_random_cloudlets(100)

# Создание и выполнение экземпляров CloudletExecution
cloudlet_execution = CloudletExecution("RoundRobin", cloudlet_list, datacenter_instance)
cloudlet_execution.execute()
data1 = cloudlet_execution.create_summary_dataset()

cloudlet_list = generate_random_cloudlets(100)
cloudlet_execution = CloudletExecution("FCFS", cloudlet_list, datacenter_instance)
cloudlet_execution.execute()
data2 = cloudlet_execution.create_summary_dataset()

cloudlet_list = generate_random_cloudlets(100)
cloudlet_execution = CloudletExecution("SJF", cloudlet_list, datacenter_instance)
cloudlet_execution.execute()
data3 = cloudlet_execution.create_summary_dataset()

cloudlet_list = generate_random_cloudlets(100)
cloudlet_execution = CloudletExecution("PS", cloudlet_list, datacenter_instance)
cloudlet_execution.execute()
data4= cloudlet_execution.create_summary_dataset()

#Объединение всех DataFrame в один
combined_data = pd.concat([data1, data2, data3,data4], ignore_index=True)
print(combined_data)
#Сохранение объединенного DataFrame в файл Excel
combined_data.to_excel("combined_cloudlet_summary.xlsx", index=False)