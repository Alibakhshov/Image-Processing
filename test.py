import random

def generate_chromosome():
    chromosome = []
    for i in range(len(nodes)):
        chromosome.append(i)
    random.shuffle(chromosome)
    return chromosome


def evaluate_chromosome(chromosome):
    total_distance = 0
    for i in range(len(chromosome) - 1):
        start_node = chromosome[i]
        end_node = chromosome[i + 1]
        total_distance += distances[(start_node, end_node)]
    return total_distance


def select_parents(population):
    parents = []
    for i in range(2):
        parent = roulette_wheel_selection(population)
        parents.append(parent)
    return parents


def roulette_wheel_selection(population):
    total_fitness = sum(evaluate_chromosome(chromosome) for chromosome in population)
    fitness_probabilities = [evaluate_chromosome(chromosome) / total_fitness for chromosome in population]
    random_value = random.random()
    probability_sum = 0
    for i, probability in enumerate(fitness_probabilities):
        probability_sum += probability
        if random_value < probability_sum:
            return population[i]


def crossover(parents):
    parent1 = parents[0]
    parent2 = parents[1]

    crossover_point = random.randint(1, len(parent1) - 2)

    child1 = []
    child2 = []

    for i in range(crossover_point):
        child1.append(parent1[i])
        child2.append(parent2[i])

    for i in range(crossover_point, len(parent1)):
        if parent2[i] not in child1:
            child1.append(parent2[i])
        if parent1[i] not in child2:
            child2.append(parent1[i])

    return child1, child2


def mutate(chromosome):
    mutation_probability = 0.1

    for i in range(len(chromosome)):
        if random.random() < mutation_probability:
            random_index = random.randint(0, len(chromosome) - 1)
            chromosome[i], chromosome[random_index] = chromosome[random_index], chromosome[i]

    return chromosome


def genetic_algorithm():
    population = []
    for i in range(100):
        population.append(generate_chromosome())

    for generation in range(100):
        new_population = []
        best_chromosome = population[0]

        for i in range(50):
            parents = select_parents(population)
            child1, child2 = crossover(parents)
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.append(child1)
            new_population.append(child2)

            # Update the best chromosome
            if evaluate_chromosome(child1) < evaluate_chromosome(best_chromosome):
                best_chromosome = child1
            if evaluate_chromosome(child2) < evaluate_chromosome(best_chromosome):
                best_chromosome = child2

        population = new_population

    best_distance = evaluate_chromosome(best_chromosome)
    print("Best distance:", best_distance)
    print("Best chromosome:", best_chromosome)


if __name__ == "__main__":
    nodes = [1, 62, 65, 89, 120, 59, 55, 110, 5, 68, 70, 200, 165, 175, 2, 88, 230, 75]
    distances = {
        (1, 62): 2,
        (1, 65): 5,
        (1, 89): 11,
        (1, 120): 13,
        (1, 59): 4,
        (1, 55): 3,
        (1, 110): 10,
        (1, 5): 8,
        (1, 68): 18,
        (1, 70): 20,
        (1, 200): 25,
    }
   
    