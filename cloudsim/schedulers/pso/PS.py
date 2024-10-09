import numpy as np
import json
from cloudsim.schedulers.pso.constants import * # Импортируем константы из файла constants.py
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

CONFIG_FILENAME = 'pso_config.json'
class Particle:
    def __init__(self, bounds):
        # Инициализируем позицию частицы случайным образом с учетом границ
        self.position = np.array([np.random.uniform(low, high) for low, high in bounds])
        # Инициализируем скорость частицы нулями
        self.velocity = np.zeros_like(self.position)
        # Инициализируем лучшую позицию частицы текущей позицией
        self.best_position = np.copy(self.position)
        # Инициализируем лучшее значение целевой функции бесконечностью
        self.best_value = float('inf')

    def update_velocity(self, global_best_position, inertia, cognitive, social):
        # Генерируем случайные числа для когнитивной и социальной составляющих скорости
        r1 = np.random.random(len(self.position))
        r2 = np.random.random(len(self.position))

        # Вычисляем когнитивную составляющую скорости
        cognitive_velocity = cognitive * r1 * (self.best_position - self.position)
        # Вычисляем социальную составляющую скорости
        social_velocity = social * r2 * (global_best_position - self.position)
        # Обновляем скорость частицы
        self.velocity = inertia * self.velocity + cognitive_velocity + social_velocity

    def update_position(self, bounds):
        # Обновляем позицию частицы
        self.position += self.velocity
        # Проверяем, не вышла ли частица за границы области поиска
        for i in range(len(self.position)):
            if self.position[i] < bounds[i][0]:
                self.position[i] = bounds[i][0]
            if self.position[i] > bounds[i][1]:
                self.position[i] = bounds[i][1]


class ParticleSwarmOptimizer:
    def __init__(self, particle_class, objective_function, config_filename=None):

        self.particle_class = particle_class  # Класс частицы, который будет использоваться
        if config_filename is None:
            self.config = self.load_or_create_config()
        else:
            self.config = self.load_or_create_config(config_filename)
        self.objective_function = objective_function  # Целевая функция, которую нужно оптимизировать
        self.bounds = self.config['bounds']  # Границы области поиска
        self.num_particles = self.config['num_particles']  # Количество частиц в рое
        self.num_iterations = self.config['num_iterations']  # Количество итераций алгоритма
        self.inertia = self.config['inertia']  # Коэффициент инерции
        self.cognitive = self.config['cognitive']  # Коэффициент когнитивной составляющей
        self.social = self.config['social']  # Коэффициент социальной составляющей
        # Создаем рой частиц
        self.swarm = [self.particle_class(self.bounds) for _ in range(self.num_particles)]
        # Инициализируем глобально лучшую позицию и значение
        self.global_best_position = np.copy(self.swarm[0].position)
        self.global_best_value = float('inf')

    def load_or_create_config(self, filename=CONFIG_FILENAME):
        if os.path.exists(filename):
            # Если файл конфигурации существует, загружаем его
            with open(filename, 'r') as f:
                config = json.load(f)
                print("Loaded configuration from", filename)
        else:
            # Если файл конфигурации не найден, создаем его с значениями по умолчанию
            with open(filename, 'w') as f:
                default_config = {DEFAULT_CONFIG_NAMES[i]: DEFAULT_PARTICLE[i] for i in range(len(DEFAULT_PARTICLE))}
                json.dump(default_config, f, indent=4)
                config = default_config
                print(f"Configuration file not found. Created default config at {filename}")
        return config

    def optimize(self, save_iterations=False, print_iterations=False):
        # Инициализируем списки для хранения лучших значений и позиций на каждой итерации, если требуется
        if save_iterations:
            best_values_per_iteration = np.zeros(self.num_iterations)
            best_positions_per_iteration = np.zeros((self.num_iterations, len(self.bounds)))

        for iteration in range(self.num_iterations):
            for particle in self.swarm:
                # Вычисляем значение целевой функции для текущей позиции частицы
                value = self.objective_function(particle.position)

                # Обновляем личный лучший результат частицы
                if value < particle.best_value:
                    particle.best_value = value
                    particle.best_position = np.copy(particle.position)

                # Обновляем глобально лучший результат
                if value < self.global_best_value:
                    self.global_best_value = value
                    self.global_best_position = np.copy(particle.position)

            # Сохраняем текущее глобально лучшее значение и позицию для этой итерации, если требуется
            if save_iterations:
                best_values_per_iteration[iteration] = self.global_best_value
                best_positions_per_iteration[iteration] = np.copy(self.global_best_position)

            # Обновляем скорость и позицию каждой частицы
            for particle in self.swarm:
                particle.update_velocity(self.global_best_position, self.inertia, self.cognitive, self.social)
                particle.update_position(self.bounds)

            # Выводим информацию о текущей итерации, если требуется
            if print_iterations:
                print(f"Iteration {iteration + 1}/{self.num_iterations}, Global Best Value: {self.global_best_value}")

        # Возвращаем лучшие значения и позиции для каждой итерации, если save_iterations=True
        if save_iterations:
            self.best_values_per_iteration = best_values_per_iteration
            self.best_positions_per_iteration = best_positions_per_iteration
            return self.global_best_position, self.global_best_value, self.best_values_per_iteration, self.best_positions_per_iteration
        else:
            return self.global_best_position, self.global_best_value, None, None

    def plot_pso_convergence(self, animated=False, gif_name="pso_convergence.gif"):
        """
        Строит график сходимости алгоритма PSO с контурным графиком целевой функции.

        Параметры:
        - objective_function: целевая функция для построения контурного графика.
        - animated: если True, создает анимированный GIF, показывающий процесс сходимости с движением частиц.
        - gif_name: имя GIF-файла для сохранения, если animated=True.
        """
        objective_function = self.objective_function
        iteration_values = self.best_values_per_iteration
        iteration_positions = self.best_positions_per_iteration

        # Создаем сетку точек для вычисления целевой функции для построения контурного графика
        x = np.linspace(self.bounds[0][0], self.bounds[0][1], 100)
        y = np.linspace(self.bounds[1][0], self.bounds[1][1], 100)
        X, Y = np.meshgrid(x, y)
        Z = np.array([[objective_function([x_val, y_val]) for x_val in x] for y_val in y])

        if animated:
            # Создаем анимированный GIF с движением частиц и глобально лучшей позицией
            fig, ax = plt.subplots()

            # Строим контурный график целевой функции
            contour = ax.contourf(X, Y, Z, levels=50, cmap='viridis')
            plt.colorbar(contour, ax=ax)

            # Инициализируем точечный график для позиций частиц
            particles = ax.scatter([], [], c='blue', label="Particles", s=50)
            global_best = ax.scatter([], [], c='red', label="Global Best", s=100, marker='x')

            ax.set_title("PSO Particle Movement and Convergence")
            ax.set_xlabel("X Position")
            ax.set_ylabel("Y Position")

            def init():
                particles.set_offsets(np.empty((0, 2)))  # Пустой массив с двумя столбцами для координат x и y
                global_best.set_offsets(np.empty((0, 2)))
                return particles, global_best

            def update(frame):
                # Обновляем позиции частиц (в этом случае только глобально лучшую позицию)
                particle_positions = np.array(iteration_positions[frame])

                # Убедимся, что позиции частиц имеют двумерную форму (N, 2)
                if particle_positions.ndim == 1:
                    particle_positions = particle_positions.reshape(-1, 2)

                particles.set_offsets(particle_positions)

                # Обновляем глобально лучшую позицию (красный крестик)
                global_best_position = np.array(iteration_positions[frame])

                # Убедимся, что глобально лучшая позиция также имеет правильную форму
                if global_best_position.ndim == 1:
                    global_best_position = global_best_position.reshape(-1, 2)

                global_best.set_offsets(global_best_position)

                return particles, global_best

            ani = animation.FuncAnimation(fig, update, frames=len(iteration_positions), init_func=init, blit=True)

            # Сохраняем анимацию как GIF
            ani.save(gif_name, writer='imagemagick', fps=5)
            print(f"Animation saved as {gif_name}")

        else:
            # Статический график с контуром и сходимостью глобально лучшего значения по итерациям
            fig, ax = plt.subplots()

            # Строим контурный график целевой функции
            contour = ax.contourf(X, Y, Z, levels=50, cmap='viridis')
            plt.colorbar(contour, ax=ax)

            # Строим график глобально лучших значений по итерациям
            plt.plot(iteration_values, marker='o', linestyle='-', color='b')
            plt.title("PSO Convergence Plot")
            plt.xlabel("Iterations")
            plt.ylabel("Global Best Value")
            plt.grid(True)
            plt.show()
