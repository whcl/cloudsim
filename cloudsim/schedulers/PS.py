import random
from cloudsim.schedulers.cloudlet_scheduler import CloudletScheduler
from simpy import AnyOf

class PSOCloudletScheduler(CloudletScheduler):
    def __init__(self, env, datacenter, num_particles, num_iterations):
        super().__init__(env, datacenter)
        self.num_particles = num_particles  # Количество частиц
        self.num_iterations = num_iterations  # Количество итераций
        self.total_execution_time = 0
        self.max_utilization = {}
        self.time_slice = 2

    class Particle:
        def __init__(self, vm, cloudlet, utilization):
            self.vm = vm  # Виртуальная машина
            self.cloudlet = cloudlet  # Клоудлет
            self.position = utilization  # Позиция частицы — утилизация ресурсов
            self.velocity = [random.uniform(-1, 1) for _ in range(3)]  # Инициализируем скорость случайными значениями
            self.best_position = self.position  # Лучшая позиция
            self.best_score = self.evaluate()  # Лучшая оценка

        def evaluate(self):
            # Функция оценки: минимизируем утилизацию ресурсов
            return sum(self.position)  # Суммируем утилизации для получения общей оценки

        def update_velocity(self, global_best_position, inertia_weight, cognitive_const, social_const):
            # Обновляем скорость частицы
            for i in range(len(self.velocity)):
                cognitive_velocity = cognitive_const * random.random() * (self.best_position[i] - self.position[i])
                social_velocity = social_const * random.random() * (global_best_position[i] - self.position[i])
                self.velocity[i] = inertia_weight * self.velocity[i] + cognitive_velocity + social_velocity

        def update_position(self):
            # Обновляем позицию частицы
            for i in range(len(self.position)):
                self.position[i] += self.velocity[i]

            # Оцениваем новую позицию
            new_score = self.evaluate()
            if new_score < self.best_score:
                self.best_position = self.position
                self.best_score = new_score

    def optimize(self, cloudlets, inertia_weight=0.5, cognitive_const=1.5, social_const=1.5):
        particles = []

        # Инициализируем частицы на основе утилизации каждой VM для каждого клоудлета
        for cloudlet in cloudlets:
            for vm in self.vm_list:
                utilization = self.get_utilization(vm, cloudlet)
                particle = self.Particle(vm, cloudlet, utilization)
                particles.append(particle)

        global_best_position = None
        global_best_score = float('inf')

        # Основной цикл PSO
        for iteration in range(self.num_iterations):
            for particle in particles:
                particle.update_velocity(global_best_position or particle.position, inertia_weight, cognitive_const, social_const)
                particle.update_position()

                if particle.best_score < global_best_score:
                    global_best_position = particle.best_position
                    global_best_score = particle.best_score

            print(f"Iteration {iteration + 1}/{self.num_iterations}, Global Best Score: {global_best_score}")

        # После оптимизации выполняем распределение клоудлетов на VM на основе глобально лучшей позиции
        for particle in particles:
            vm = particle.vm
            cloudlet = particle.cloudlet
            self.env.process(self.schedule_cloudlet(cloudlet))

    def schedule_cloudlets(self, cloudlets):
        remaining_cloudlets = list(cloudlets)
        while remaining_cloudlets:
            batch = remaining_cloudlets[:len(self.vm_list)]  # Количество клоудлетов = Количество ВМ
            remaining_cloudlets = remaining_cloudlets[len(batch):]

            completion_events = [self.env.process(self.schedule_cloudlet(cloudlet)) for cloudlet in batch]
            yield AnyOf(self.env, completion_events)

        # Печатаем общее время выполнения и использование ресурсов ВМ после выполнения всех клоудлетов

    def print_summary(self):
        print(f"\nTotal Execution Time: {self.total_execution_time}")
        for vm_id, utilization in self.max_utilization.items():
            print(
                f"\nVM {vm_id} utilization:\n {utilization[0] * 100}% PEs\n, {utilization[1] * 100}% RAM\n, {utilization[2] * 100}% Storage"
            )

    def schedule_cloudlet(self, cloudlet):
        while cloudlet.length > 0:
            for selected_vm in self.free_vms[:]:
                if self.has_enough_resources(selected_vm, cloudlet):
                    self.free_vms.remove(selected_vm)
                    cloudlet.set_vm(selected_vm)
                    self.running_vms.append(selected_vm)
                    self.max_utilization[selected_vm.get_id()] = max(
                        self.max_utilization.get(selected_vm.get_id(), [0, 0, 0]),
                        self.get_utilization(selected_vm, cloudlet)
                    )

                    print(
                        f"Cloudlet {cloudlet.cloudlet_id} starts execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}"
                    )

                    execution_time = min(self.time_slice, cloudlet.length)
                    yield self.env.timeout(execution_time)
                    cloudlet.length -= execution_time

                    print(
                        f"Cloudlet {cloudlet.cloudlet_id} completes execution on VM {cloudlet.get_vm().get_id()} at {self.env.now}"
                    )

                    self.running_vms.remove(selected_vm)
                    self.free_vms.append(selected_vm)

                    self.total_execution_time += execution_time
                    self.print_summary()  # Перемещено сюда
                    break
            else:
                yield self.env.timeout(1)
