"""
Vehicle Maintenance Scheduler Microservice

This module implements an efficient knapsack-based algorithm to determine the optimal
subset of vehicles to service, maximizing the total operational impact score within
the available mechanic-hour budget.
"""

import os
import json
import requests
import sys
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Add parent directory to path to import logging middleware
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from logging_middleware.logger import Log


class VehicleMaintenanceScheduler:
    """Determines optimal vehicle maintenance schedule using dynamic programming."""
    
    def __init__(self, auth_token: str):
        """
        Initialize the scheduler with authentication token.
        
        Args:
            auth_token: JWT token for API authentication
        """
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
        }
        self.depot_api = "http://20.207.122.201/evaluation-service/depots"
        self.vehicles_api = "http://20.207.122.201/evaluation-service/vehicles"
    
    def fetch_depots(self) -> List[Dict]:
        """
        Fetch all available depots.
        
        Returns:
            List of depot dictionaries
        """
        try:
            Log("backend", "info", "repository", "Fetching depot info")
            response = requests.get(self.depot_api, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            Log("backend", "info", "repository", f"Fetched {len(data.get('depots', []))} depot(s)")
            return data.get("depots", [])
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching depots: {e}"
            Log("backend", "error", "repository", error_msg)
            return []
    
    def fetch_vehicles(self) -> List[Dict]:
        """
        Fetch all vehicles requiring maintenance.
        
        Returns:
            List of vehicle dictionaries with duration and impact scores
        """
        try:
            Log("backend", "debug", "repository", "Fetching vehicles")
            response = requests.get(self.vehicles_api, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            Log("backend", "info", "repository", f"Fetched {len(data.get('vehicles', []))} vehicle(s)")
            return data.get("vehicles", [])
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching vehicles: {e}"
            Log("backend", "error", "repository", error_msg)
            return []
    
    def solve_knapsack(
        self, 
        vehicles: List[Dict], 
        budget: float
    ) -> Tuple[List[Dict], float, float]:
        """
        Solve the 0/1 knapsack problem using dynamic programming.
        
        Maximizes total importance score while staying within the budget constraint.
        
        Args:
            vehicles: List of vehicles with 'Duration' and 'Impact' keys
            budget: Available mechanic-hours (knapsack capacity)
        
        Returns:
            Tuple of (selected_vehicles, total_duration, total_importance_score)
        """
        n = len(vehicles)
        budget = int(budget)
        
        # DP table: dp[i][w] = max importance score using first i vehicles with w hours
        dp = [[0] * (budget + 1) for _ in range(n + 1)]
        
        # Fill DP table
        for i in range(1, n + 1):
            vehicle = vehicles[i - 1]
            duration = int(vehicle.get("Duration", 0))
            impact = vehicle.get("Impact", 0)
            
            for w in range(budget + 1):
                # Option 1: Do not include this vehicle
                dp[i][w] = dp[i - 1][w]
                
                # Option 2: Include this vehicle if it fits
                if duration <= w:
                    dp[i][w] = max(dp[i][w], dp[i - 1][w - duration] + impact)
        
        # Backtrack to find selected vehicles
        selected = []
        w = budget
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                vehicle = vehicles[i - 1]
                selected.append(vehicle)
                duration = int(vehicle.get("Duration", 0))
                w -= duration
        
        selected.reverse()
        
        total_duration = sum(int(v.get("Duration", 0)) for v in selected)
        total_importance = sum(v.get("Impact", 0) for v in selected)
        
        return selected, total_duration, total_importance
    
    def schedule(self) -> Dict:
        """
        Execute the complete scheduling workflow.
        
        Returns:
            Dictionary containing scheduling results
        """
        Log("backend", "info", "service", "Starting scheduling workflow")
        
        depots = self.fetch_depots()
        
        if not depots:
            error_msg = "No depots found"
            Log("backend", "error", "service", error_msg)
            return {"error": "No depots available"}
        
        depot = depots[0]
        mechanic_hours = depot.get("MechanicHours", 0)
        depot_id = depot.get("ID", "Unknown")
        
        Log("backend", "info", "service", f"Depot {depot_id}: {mechanic_hours}h available")
        
        vehicles = self.fetch_vehicles()
        
        if not vehicles:
            error_msg = "No vehicles found"
            Log("backend", "error", "service", error_msg)
            return {"error": "No vehicles available"}
        
        Log("backend", "info", "service", f"Found {len(vehicles)} vehicles")
        
        Log("backend", "debug", "service", "Running knapsack algorithm")
        selected_vehicles, total_duration, total_importance = self.solve_knapsack(
            vehicles, 
            mechanic_hours
        )
        
        Log("backend", "info", "service", f"Selected {len(selected_vehicles)} vehicles")
        
        results = {
            "depot_id": depot_id,
            "available_mechanic_hours": mechanic_hours,
            "total_vehicles_available": len(vehicles),
            "vehicles_selected": len(selected_vehicles),
            "total_duration_used": total_duration,
            "total_importance_score": total_importance,
            "efficiency_percentage": (total_duration / mechanic_hours * 100) if mechanic_hours > 0 else 0,
            "selected_vehicles": [
                {
                    "task_id": v.get("TaskID"),
                    "duration": v.get("Duration"),
                    "impact": v.get("Impact")
                }
                for v in selected_vehicles
            ]
        }
        
        Log("backend", "info", "service", f"Impact: {total_importance}, Duration: {total_duration}h")
        
        return results


def main():
    """Main entry point for the scheduler."""
    load_dotenv()
    auth_token = os.getenv("AUTH_TOKEN")
    
    if not auth_token:
        error_msg = "AUTH_TOKEN not found"
        Log("backend", "error", "config", error_msg)
        print(f"Error: {error_msg}")
        return
    
    Log("backend", "info", "service", "Scheduler service started")
    
    scheduler = VehicleMaintenanceScheduler(auth_token)
    results = scheduler.schedule()
    
    if "error" in results:
        Log("backend", "error", "service", f"Scheduling failed: {results['error']}")
        print(f"Error: {results['error']}")
        return
    
    print("\nVEHICLE MAINTENANCE SCHEDULING RESULTS")
    print(f"Depot ID: {results.get('depot_id')}")
    print(f"Available Mechanic-Hours: {results.get('available_mechanic_hours')}")
    print(f"Total Vehicles Found: {results.get('total_vehicles_available')}")
    print(f"Vehicles Selected: {results.get('vehicles_selected')}")
    print(f"Total Duration Used: {results.get('total_duration_used')} hours")
    print(f"Total Importance Score: {results.get('total_importance_score')}")
    print(f"Budget Utilization: {results.get('efficiency_percentage'):.2f}%")
    print("="*60)
    
    print("\nSelected Vehicles:")
    for i, vehicle in enumerate(results.get('selected_vehicles', []), 1):
        print(f"{i}. TaskID: {vehicle['task_id']}, "
              f"Duration: {vehicle['duration']}h, Impact: {vehicle['impact']}")
    
    # Save results to JSON
    with open("scheduling_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    Log("backend", "info", "utils", "Results saved to JSON")
    print("\nResults saved to scheduling_results.json")
    Log("backend", "info", "service", "Scheduler completed")


if __name__ == "__main__":
    main()
