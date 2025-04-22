import numpy as np
import time
from functools import partial
import multiprocessing
import cupy as cp
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import cupy as cp  # Assuming cupy is used for GPU acceleration

app = FastAPI()


# 1. set_cost_matrix Endpoint

app = FastAPI()

# Assuming a global variable to store the matrices and other problem data
# This is a simple approach. In production, consider using a more robust data management system
global_problem_data = {
    "cost_matrix": None,
    "time_matrix": None,
    # Add other necessary data fields as needed
}


class CostMatrix(BaseModel):
    matrix: list[list[float]]


@app.post("/set_cost_matrix")
async def set_cost_matrix(cost_matrix: CostMatrix):
    try:
        # Convert the cost matrix to a CuPy array for GPU acceleration
        gpu_cost_matrix = cp.array(cost_matrix.matrix)

        # Store the GPU-accelerated cost matrix in our global problem data
        global_problem_data["cost_matrix"] = gpu_cost_matrix

        return {"message": "Cost matrix set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. set_travel_time_matrix Endpoint


class TimeMatrix(BaseModel):
    matrix: list[list[float]]


@app.post("/set_travel_time_matrix")
async def set_travel_time_matrix(time_matrix: TimeMatrix):
    try:
        # Convert the travel time matrix to a CuPy array for GPU acceleration
        gpu_time_matrix = cp.array(time_matrix.matrix)

        # Store the GPU-accelerated time matrix in our global problem data
        global_problem_data["time_matrix"] = gpu_time_matrix

        return {"message": "Travel time matrix set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. set_task_data Endpoint

class TaskData(BaseModel):
    task_locations: list[int]
    demand: list[list[int]]
    service_times: list[float]
    task_time_windows: list[list[int]]  # Optional, if time windows are required


@app.post("/set_task_data")
async def set_task_data(task_data: TaskData):
    try:
        # Validate and transform the input data as required for the optimization algorithm
        # For example, you might need to transform the data into a specific format or structure

        # Store the task data in our global problem data
        # This includes the locations, demand at each location, service times, and optionally time windows
        global_problem_data["task_data"] = {
            "locations": task_data.task_locations,
            "demand": task_data.demand,
            "service_times": task_data.service_times,
            "time_windows": task_data.task_time_windows  # Optional
        }

        return {"message": "Task data set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. set_fleet_data Endpoint

class FleetData(BaseModel):
    vehicle_ids: list[int]
    capacities: list[int]
    availability_times: list[list[int]]
    # Additional fields can be added as needed


@app.post("/set_fleet_data")
async def set_fleet_data(fleet_data: FleetData):
    try:
        # Process and validate the fleet data
        # For example, ensure that the number of vehicles matches the number of capacities and availability times

        if not (len(fleet_data.vehicle_ids) == len(fleet_data.capacities) == len(fleet_data.availability_times)):
            raise ValueError("Mismatch in the length of fleet data lists")

        # Store the fleet data in our global problem data
        global_problem_data["fleet_data"] = {
            "vehicle_ids": fleet_data.vehicle_ids,
            "capacities": fleet_data.capacities,
            "availability_times": fleet_data.availability_times,
            # Include additional attributes here
        }

        return {"message": "Fleet data set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5. set_solver_config Endpoint

class SolverConfig(BaseModel):
    time_limit: float
    number_of_climbers: int
    objectives: dict  # Assuming objectives is a dictionary, adjust as needed
    verbose_mode: bool
    error_logging: bool

    # You can add validations within the model if needed
    # Example:
    # @validator('time_limit')
    # def time_limit_must_be_positive(cls, v):
    #     assert v > 0, 'time_limit must be positive'
    #     return v


@app.post("/set_solver_config")
async def set_solver_config(solver_config: SolverConfig):
    try:
        # Validate the solver configuration data
        if solver_config.time_limit <= 0:
            raise ValueError("time_limit must be positive")
        if solver_config.number_of_climbers <= 0:
            raise ValueError("number_of_climbers must be positive")

        # Store the solver configuration in our global problem data
        global_problem_data["solver_config"] = {
            "time_limit": solver_config.time_limit,
            "number_of_climbers": solver_config.number_of_climbers,
            "objectives": solver_config.objectives,
            "verbose_mode": solver_config.verbose_mode,
            "error_logging": solver_config.error_logging
        }

        return {"message": "Solver configuration set successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. get_optimized_routes Endpoint


@app.get("/get_optimized_routes")
async def get_optimized_routes():
    try:
        # Ensure all required data is present
        if not all(key in global_problem_data for key in ["cost_matrix", "time_matrix", "task_data", "fleet_data", "solver_config"]):
            raise ValueError("Not all required data is set for optimization")

        # Extract the data from global_problem_data
        cost_matrix = global_problem_data["cost_matrix"]
        time_matrix = global_problem_data["time_matrix"]
        task_data = global_problem_data["task_data"]
        fleet_data = global_problem_data["fleet_data"]
        solver_config = global_problem_data["solver_config"]

        # Optimization Logic
        # This is where the CVRPTW algorithm is implemented or called.
        # The algorithm should consider all the constraints and objectives based on the provided data.
        # For example, you might use a third-party library or a custom algorithm for this purpose.
        # The logic will likely involve GPU-accelerated computations if using libraries like CuPy or RAPIDS.

        # Assuming a function `optimize_routes` performs the CVRPTW optimization and returns the results
        optimized_routes, solution_details = optimize_routes(cost_matrix, time_matrix, task_data, fleet_data, solver_config)

        return {"optimized_routes": optimized_routes, "solution_details": solution_details}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def compute_cost_on_gpu(vehicle_id, tasks, cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, current_time):

    # tasks = cp.array(tasks, dtype=cp.int32)  # Explicitly specify integer data type
    tasks = cp.array(list(tasks), dtype=cp.int32)
    # Extract relevant data for the specified vehicle
    vehicle_capacity = cp_fleet_data['capacities'][vehicle_id]
    vehicle_current_location = cp_fleet_data['locations'][vehicle_id]

    # Calculate travel costs for each task
    travel_costs = cp_cost_matrix[vehicle_current_location, tasks]
    # Capacity constraints
    task_demands = cp_task_data['demands'][tasks]
    over_capacity = task_demands > vehicle_capacity
    travel_costs = cp.where(over_capacity, cp.inf, travel_costs)
    # 추가된 로그 출력
    if any(over_capacity.get()):
        print(f"Vehicle {vehicle_id}: Some tasks exceed capacity")

    # Time window constraints
    task_earliest_times = cp_task_data['earliest_times'][tasks]
    task_latest_times = cp_task_data['latest_times'][tasks]
    estimated_arrival_times = current_time + cp_time_matrix[vehicle_current_location, tasks]
    early_arrival = estimated_arrival_times < task_earliest_times
    late_arrival = estimated_arrival_times > task_latest_times
    travel_costs = cp.where(early_arrival | late_arrival, cp.inf, travel_costs)
    # 추가된 로그 출력
    if any(early_arrival.get()) or any(late_arrival.get()):
        print(f"Vehicle {vehicle_id}: Time window constraints violated")

    return travel_costs


def convert_to_gpu_format(data):
    gpu_data = {}
    for key, value in data.items():
        if isinstance(value, list) or isinstance(value, np.ndarray):
            gpu_data[key] = cp.array(value)
        else:
            gpu_data[key] = value
    return gpu_data


def find_best_task_on_gpu(vehicle_id, tasks, cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, route_sizes, route_service_times, solver_config, current_time):
    if not tasks:
        return None, float('inf')
    # Compute the costs considering the current time
    costs = compute_cost_on_gpu(vehicle_id, tasks, cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, current_time)
    # 로그를 위한 verbose_mode 확인
    verbose_mode = solver_config.get('verbose_mode', False)
    if verbose_mode:
        print(f"Vehicle {vehicle_id}: Initial costs for tasks: {costs.get()}")
    # Modify costs based on objectives from the solver configuration
    for i, task in enumerate(tasks):
        if solver_config['objectives']['variance_route_size']:
            costs[i] += route_sizes[vehicle_id] * solver_config['objectives']['variance_route_size']
        if solver_config['objectives']['variance_route_service_time']:
            costs[i] += route_service_times[vehicle_id] * solver_config['objectives']['variance_route_service_time']

    # 최적의 작업과 비용을 찾음
    best_task_index = cp.argmin(costs)
    best_cost = costs[best_task_index]  # 마찬가지로 파이썬 정수로 변환
    best_task = tasks[best_task_index.get()] if best_cost < float('inf') else None
    # 할당 가능한 작업이 있는지 확인
    if best_cost < float('inf'):
        if verbose_mode:
            print(f"Vehicle {vehicle_id}: Assigning task {best_task} with cost {best_cost}")
    else:
        if verbose_mode:
            print(f"Vehicle {vehicle_id}: No feasible task found")
    return best_task, best_cost.get()  # Transfer data back to CPU


def greedy_heuristic(cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, solver_config):
    start_time = time.time()  # 시작 시간 기록
    time_limit = solver_config['time_limit']
    # Initialize routes and other metrics for each vehicle
    routes = {vehicle_id: [] for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    route_sizes = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    route_service_times = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    current_times = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}  # Track current time for each vehicle

    unassigned_tasks = set(range(len(cp_task_data['locations'])))
    tasks_assigned = False
    while unassigned_tasks:
        if time.time() - start_time > time_limit:
            break
        for vehicle_id in routes:
            best_task, best_cost = find_best_task_on_gpu(vehicle_id, list(unassigned_tasks), cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, route_sizes, route_service_times, solver_config, current_times[vehicle_id])
            if solver_config.get('verbose_mode', False):
                print(f"Vehicle {vehicle_id} - Best Task: {best_task}, Cost: {best_cost}")
            if best_task is not None:
                tasks_assigned = True
                routes[vehicle_id].append(best_task)
                # Update route sizes
                route_sizes[vehicle_id] += 1
                # Check if best_task is within the range of service_times
                if best_task < len(cp_task_data['service_times']):
                    route_service_times[vehicle_id] += cp_task_data['service_times'][best_task].get()  # Use .get() to convert to Python integer
                    # Update the current time for the vehicle
                    travel_time_to_task = cp_time_matrix[vehicle_id, best_task].get()  # Convert to Python integer
                    current_times[vehicle_id] += travel_time_to_task + cp_task_data['service_times'][best_task].get()
                unassigned_tasks.remove(best_task)
        if not tasks_assigned:
            break  # No tasks were assigned in this iteration
        tasks_assigned = False  # Reset for next iteration
    if solver_config.get('verbose_mode', False):
        print(f"Final Routes: {routes}")
    return routes


def greedy_heuristic_parallel(cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, solver_config, task_subset):
    # multiprocessing.set_start_method('spawn')
    start_time = time.time()  # 시작 시간 기록
    time_limit = solver_config['time_limit']
    # Initialize routes and other metrics for each vehicle
    routes = {vehicle_id: [] for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    route_sizes = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    route_service_times = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}
    current_times = {vehicle_id: 0 for vehicle_id in range(len(cp_fleet_data['vehicle_ids']))}  # Track current time for each vehicle

    unassigned_tasks = set(task_subset.tolist()) if isinstance(task_subset, np.ndarray) else set(task_subset)
    tasks_assigned = False
    while unassigned_tasks:
        if time.time() - start_time > time_limit:
            break
        for vehicle_id in routes:
            best_task, best_cost = find_best_task_on_gpu(vehicle_id, list(unassigned_tasks), cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, route_sizes, route_service_times, solver_config, current_times[vehicle_id])
            if solver_config['verbose_mode']:
                print(f"Vehicle {vehicle_id} - Best Task: {best_task}, Cost: {best_cost}")
            if best_task is not None:
                tasks_assigned = True
                routes[vehicle_id].append(best_task)
                # Update route sizes
                route_sizes[vehicle_id] += 1
                # Check if best_task is within the range of service_times
                if best_task < len(cp_task_data['service_times']):
                    route_service_times[vehicle_id] += cp_task_data['service_times'][best_task].get()  # Use .get() to convert to Python integer
                    # Update the current time for the vehicle
                    travel_time_to_task = cp_time_matrix[vehicle_id, best_task].get()  # Convert to Python integer
                    current_times[vehicle_id] += travel_time_to_task + cp_task_data['service_times'][best_task].get()
                unassigned_tasks.remove(best_task)
        if not tasks_assigned:
            break  # No tasks were assigned in this iteration
        tasks_assigned = False  # Reset for next iteration

    if solver_config['verbose_mode']:
        print(f"Final Routes: {routes}")
    return routes


def optimize_routes(cost_matrix, time_matrix, task_data, fleet_data, solver_config):
    cp_cost_matrix = cp.array(cost_matrix)
    cp_time_matrix = cp.array(time_matrix)
    gpu_task_data = convert_to_gpu_format(task_data)
    gpu_fleet_data = convert_to_gpu_format(fleet_data)

    optimized_routes = greedy_heuristic(cp_cost_matrix, cp_time_matrix, gpu_task_data, gpu_fleet_data, solver_config)

    return optimized_routes


def optimize_routes_parallel(cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, solver_config):
    num_climbers = solver_config['number_of_climbers']
    task_sets = split_tasks_for_climbers(cp_task_data['locations'], num_climbers)
    partial_greedy_heuristic = partial(greedy_heuristic_parallel, cp_cost_matrix, cp_time_matrix, cp_task_data, cp_fleet_data, solver_config)
    with multiprocessing.Pool(processes=num_climbers) as pool:
        results = pool.map(partial_greedy_heuristic, task_sets)
    combined_routes = combine_results_from_climbers(results)
    return combined_routes


def split_tasks_for_climbers(tasks, num_climbers):
    task_set_size = len(tasks) // num_climbers
    task_sets = [tasks[i * task_set_size:(i + 1) * task_set_size].tolist() for i in range(num_climbers)]

    # 마지막 클라이머에 남은 작업을 할당
    if len(tasks) % num_climbers != 0:
        task_sets[-1].extend(tasks[-(len(tasks) % num_climbers):].tolist())

    return task_sets


def combine_results_from_climbers(results):
    # Combine the routes from all climbers
    # Assuming each climber worked on a distinct set of tasks
    combined_routes = {}
    for result in results:
        for vehicle_id, route in result.items():
            if vehicle_id in combined_routes:
                combined_routes[vehicle_id].extend(route)
            else:
                combined_routes[vehicle_id] = route
    return combined_routes


def create_test_data():
    # Adjusted example test data for a vehicle routing problem
    cost_matrix = [
        [0, 10, 15, 20],  # Distances from location 0
        [10, 0, 25, 30],  # Distances from location 1
        [15, 25, 0, 10],  # Distances from location 2
        [20, 30, 10, 0]   # Distances from location 3
    ]
    time_matrix = [
        [0, 12, 18, 24],  # Travel times from location 0
        [12, 0, 30, 36],  # Travel times from location 1
        [18, 30, 0, 12],  # Travel times from location 2
        [24, 36, 12, 0]   # Travel times from location 3
    ]
    task_data = {
        'locations': [1, 2, 3],   # Task locations
        'demands': [2, 3, 1],     # Task demands
        'service_times': [5, 5, 5],  # Service times at each task
        'earliest_times': [0, 0, 0],  # Earliest start times
        'latest_times': [100, 100, 100]  # Latest start times
    }
    fleet_data = {
        'vehicle_ids': [0, 1],
        'capacities': [5, 5],      # Vehicle capacities
        'locations': [0, 0]        # Starting locations for all vehicles
    }
    solver_config = {
        'time_limit': 10,          # Time limit in seconds
        'number_of_climbers': 2,
        'objectives': {
            "vehicle": 0,
            "cost": 1,
            'variance_route_size': 1000,
            'variance_route_service_time': 1000
        },
        'verbose_mode': True,
        'error_logging': True
    }
    return cost_matrix, time_matrix, task_data, fleet_data, solver_config

# Expected Outcomes:
# This test data represents a simple scenario with three tasks and two vehicles.
# Each task has a service time of 5 minutes, and the latest time for each task is set generously to 100.
# The solver is expected to assign tasks to vehicles while considering the distance, capacity, and time windows.
# The exact outcome depends on the implementation of the routing algorithm, but ideally, it should balance the load between the two vehicles and respect the capacity and time constraints.


def create_simple_test_data():
    cost_matrix = [[0, 1, 2], [1, 0, 2], [2, 2, 0]]  # 간단한 거리
    time_matrix = [[0, 5, 10], [5, 0, 10], [10, 10, 0]]  # 간단한 이동 시간
    task_data = {
        'locations': [1, 2],  # 작업 위치
        'demands': [1, 1],  # 작업 요구량
        'service_times': [5, 5],  # 각 작업의 서비스 시간
        'earliest_times': [0, 0],  # 최소 시작 시간
        'latest_times': [100, 100]  # 최대 시작 시간
    }
    fleet_data = {
        'vehicle_ids': [0, 1],
        'capacities': [5, 5],
        'locations': [0, 0]  # 모든 차량이 위치 0에서 시작
    }
    solver_config = {
        'time_limit': 30,
        'number_of_climbers': 2,
        'objectives': {
            "vehicle": 0,
            "cost": 1,
            'variance_route_size': 1000,
            'variance_route_service_time': 1000
        },
        'verbose_mode': True,
        'error_logging': True
    }
    return cost_matrix, time_matrix, task_data, fleet_data, solver_config


def run_serial_version():
    print('run_serial_version 실행')
    cost_matrix, time_matrix, task_data, fleet_data, solver_config = create_test_data()
    optimized_routes = optimize_routes(cost_matrix, time_matrix, task_data, fleet_data, solver_config)
    print("Optimized Routes (Serial):", optimized_routes)


def run_parallel_version():
    print('run_parallel_version 실행')
    multiprocessing.set_start_method('spawn')  # or 'forkserver'
    cost_matrix, time_matrix, task_data, fleet_data, solver_config = create_test_data()
    solver_config['number_of_climbers'] = 4  # Example number of climbers for parallel execution
    optimized_routes_parallel = optimize_routes_parallel(cp.array(cost_matrix), cp.array(time_matrix), convert_to_gpu_format(task_data), convert_to_gpu_format(fleet_data), solver_config)
    print("Optimized Routes (Parallel):", optimized_routes_parallel)


def main():
    run_parallel_version()
    run_serial_version()


if __name__ == "__main__":
    # multiprocessing.set_start_method('spawn')  # or 'forkserver'
    main()
