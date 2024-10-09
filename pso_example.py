from cloudsim.schedulers.pso.PS import *


def quadratic_objective_function(x):
    return x[0] ** 2 + x[1] ** 2 + 50  # Простая квадратичная функция


pso = ParticleSwarmOptimizer(Particle, quadratic_objective_function)
best_position, best_value, iteration_values, iteration_positions = pso.optimize(save_iterations=True,
                                                                                print_iterations=False)
print("Best Position:", best_position)
print("Best Value:", best_value)
pso.plot_pso_convergence(animated=True)
