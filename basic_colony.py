import pants
import math
import random
import numpy as np
import matplotlib.pyplot as plt
#set seed for reproducibility
np.random.seed(42)
# Generate random nodes
nodes = np.random.uniform(-100, 100, size=(20, 2)).tolist()

def plot_all_solutions(nodes, solutions, best_solution):
    plt.figure(figsize=(10, 6))
    plt.scatter(*zip(*nodes), c='blue', marker='o')  # Plot nodes
    
    # Plot all solutions with varying transparency
    for i, solution in enumerate(solutions):
        tour = solution.tour + [solution.tour[0]]  # Make the tour circular
        alpha = 0.1 + (0.9 * (i / len(solutions)))  # Vary transparency
        plt.plot(*zip(*tour), '-ro', alpha=alpha)
    
    # Highlight the best solution
    best_tour = best_solution.tour + [best_solution.tour[0]]
    
    plt.plot(*zip(*best_tour), '-go', alpha=1.0, linewidth=2)   
    plt.title(f"All Solutions with Best Solution Highlighted")
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    #add legend showing which color of plot means what
    plt.legend(["Best Solution", "All Solutions", "Nodes"], loc='upper right')
    

    plt.grid(True)
    plt.show()


def main():
# Define the Euclidean distance function
    def euclidean(a, b):
        return math.sqrt(pow(a[1] - b[1], 2) + pow(a[0] - b[0], 2))

    # Create the world and solver
    world = pants.World(nodes, euclidean)
    solver = pants.Solver()
    solutions = list(solver.solutions(world))  # Convert generator to list

    # Function to plot all solutions

    # Find the best solution
    best_solution = solver.solve(world)
    return best_solution,solutions
if __name__ == '__main__':
    best_list = []
    for i in range(100):
        
        best_solution,_= main()
        print(f"Best distance: {best_solution.distance:.2f}")
        # print(f"Best tour: {best_solution.tour}")
        best_list.append(best_solution.distance)
    #plot best list distribution kde smooth curve use seaborn
    import seaborn as sns
    sns.kdeplot(best_list, fill=True)
    plt.title("Distribution of Best Solutions")
    plt.xlabel("Distance")
    plt.ylabel("Density")
    plt.show()
    #plot all solutions
    best_solution,solutions = main()
    plot_all_solutions(nodes, solutions, best_solution)
    print(f"Best distance: {best_solution.distance:.2f}")
    print(f"Best tour: {best_solution.tour}")
    print("Done")

