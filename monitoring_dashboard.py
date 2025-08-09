"""
Prometheus Monitoring Dashboard for ML API
This script creates a simple monitoring dashboard showing key metrics.
"""

import requests
import time
import json
import threading
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np

class MLAPIMonitor:
    """Monitor ML API metrics and create a dashboard"""
    
    def __init__(self, api_url="http://localhost:8000", max_points=50):
        self.api_url = api_url
        self.max_points = max_points
        
        # Data storage for metrics
        self.timestamps = deque(maxlen=max_points)
        self.prediction_counts = deque(maxlen=max_points)
        self.response_times = deque(maxlen=max_points)
        self.predictions = deque(maxlen=max_points)
        
        # Sample data for generating predictions
        self.sample_data = [
            {
                "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984127,
                "AveBedrms": 1.023810, "Population": 322.0, "AveOccup": 2.555556,
                "Latitude": 37.88, "Longitude": -122.23
            },
            {
                "MedInc": 3.2411, "HouseAge": 52.0, "AveRooms": 5.817352,
                "AveBedrms": 1.073446, "Population": 2401.0, "AveOccup": 2.109842,
                "Latitude": 37.86, "Longitude": -122.22
            },
            {
                "MedInc": 5.6431, "HouseAge": 52.0, "AveRooms": 6.281853,
                "AveBedrms": 1.081081, "Population": 496.0, "AveOccup": 2.802260,
                "Latitude": 37.85, "Longitude": -122.24
            }
        ]
        
        self.running = True
        self.prediction_counter = 0
    
    def check_api_health(self):
        """Check if API is running and healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_prometheus_metrics(self):
        """Fetch Prometheus metrics from API"""
        try:
            response = requests.get(f"{self.api_url}/metrics", timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except:
            return None
    
    def make_prediction(self):
        """Make a prediction to generate metrics"""
        try:
            sample = np.random.choice(self.sample_data)
            start_time = time.time()
            response = requests.post(f"{self.api_url}/predict", json=sample, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                return {
                    'prediction': result['prediction'],
                    'response_time': response_time,
                    'success': True
                }
            return {'success': False}
        except Exception as e:
            print(f"Prediction error: {e}")
            return {'success': False}
    
    def data_generator(self):
        """Generate data in background thread"""
        while self.running:
            try:
                # Make a prediction every 2 seconds
                result = self.make_prediction()
                
                if result['success']:
                    now = datetime.now()
                    self.timestamps.append(now)
                    self.prediction_counter += 1
                    self.prediction_counts.append(self.prediction_counter)
                    self.response_times.append(result['response_time'])
                    self.predictions.append(result['prediction'])
                    
                    print(f"[{now.strftime('%H:%M:%S')}] Prediction #{self.prediction_counter}: "
                          f"${result['prediction']:.2f}, Response: {result['response_time']:.1f}ms")
                
                time.sleep(2)
            except Exception as e:
                print(f"Data generation error: {e}")
                time.sleep(5)
    
    def create_dashboard(self):
        """Create matplotlib dashboard"""
        plt.style.use('dark_background')
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('ML API Monitoring Dashboard - California Housing Predictions', 
                     fontsize=16, fontweight='bold')
        
        def animate(frame):
            # Clear all axes
            for ax in [ax1, ax2, ax3, ax4]:
                ax.clear()
            
            if len(self.timestamps) > 0:
                times = [t.strftime('%H:%M:%S') for t in list(self.timestamps)]
                
                # Plot 1: Prediction Count Over Time
                ax1.plot(range(len(self.prediction_counts)), list(self.prediction_counts), 
                        'g-', linewidth=2, marker='o', markersize=4)
                ax1.set_title('Total Predictions Over Time', fontweight='bold')
                ax1.set_ylabel('Prediction Count')
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45)
                
                # Plot 2: Response Times
                ax2.plot(range(len(self.response_times)), list(self.response_times), 
                        'b-', linewidth=2, marker='s', markersize=4)
                ax2.set_title('API Response Times', fontweight='bold')
                ax2.set_ylabel('Response Time (ms)')
                ax2.grid(True, alpha=0.3)
                
                # Plot 3: Prediction Values Distribution
                predictions_list = list(self.predictions)
                ax3.hist(predictions_list, bins=10, color='orange', alpha=0.7, edgecolor='white')
                ax3.set_title('Prediction Values Distribution', fontweight='bold')
                ax3.set_xlabel('Housing Price (hundreds of thousands)')
                ax3.set_ylabel('Frequency')
                ax3.grid(True, alpha=0.3)
                
                # Plot 4: Recent Predictions
                recent_times = times[-10:] if len(times) >= 10 else times
                recent_preds = list(self.predictions)[-10:] if len(self.predictions) >= 10 else list(self.predictions)
                
                if recent_preds:
                    bars = ax4.bar(range(len(recent_preds)), recent_preds, 
                                  color='purple', alpha=0.7, edgecolor='white')
                    ax4.set_title('Recent 10 Predictions', fontweight='bold')
                    ax4.set_ylabel('Housing Price')
                    ax4.set_xlabel('Recent Predictions')
                    ax4.grid(True, alpha=0.3)
                    
                    # Add value labels on bars
                    for i, bar in enumerate(bars):
                        height = bar.get_height()
                        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                               f'${height:.2f}', ha='center', va='bottom', fontsize=8)
            
            # Add status information
            status_text = f"Status: {'🟢 Online' if self.check_api_health() else '🔴 Offline'}\n"
            status_text += f"Total Predictions: {self.prediction_counter}\n"
            status_text += f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
            
            fig.text(0.02, 0.02, status_text, fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="navy", alpha=0.8))
            
            plt.tight_layout()
        
        # Start animation
        ani = animation.FuncAnimation(fig, animate, interval=2000, cache_frame_data=False)
        
        # Start data generation thread
        data_thread = threading.Thread(target=self.data_generator, daemon=True)
        data_thread.start()
        
        plt.show()
        
        # Stop when window is closed
        self.running = False
    
    def print_current_metrics(self):
        """Print current Prometheus metrics"""
        print("\n" + "="*60)
        print("CURRENT PROMETHEUS METRICS")
        print("="*60)
        
        metrics = self.get_prometheus_metrics()
        if metrics:
            # Parse and display key metrics
            lines = metrics.split('\n')
            important_metrics = []
            
            for line in lines:
                if line.startswith('predictions_total') or \
                   line.startswith('prediction_duration_seconds') or \
                   line.startswith('python_info') or \
                   'http_requests' in line:
                    important_metrics.append(line)
            
            if important_metrics:
                for metric in important_metrics:
                    print(metric)
            else:
                print("No specific ML metrics found, showing raw metrics:")
                print(metrics[:500] + "..." if len(metrics) > 500 else metrics)
        else:
            print("❌ Could not fetch metrics (API may be down)")
        
        print("="*60)


def main():
    """Main function to run the monitoring dashboard"""
    print("🔍 ML API Prometheus Monitoring Dashboard")
    print("="*50)
    
    monitor = MLAPIMonitor()
    
    # Check if API is running
    if not monitor.check_api_health():
        print("❌ API is not running at http://localhost:8000")
        print("   Please start the API first: python run_api.py")
        return
    
    print("✅ API is running and healthy")
    
    # Show current metrics
    monitor.print_current_metrics()
    
    # Ask user what they want to do
    print("\nChoose monitoring option:")
    print("1. Live Dashboard (matplotlib)")
    print("2. Print metrics and exit")
    print("3. Generate sample data and show metrics")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting live monitoring dashboard...")
        print("   - Dashboard will update every 2 seconds")
        print("   - API predictions will be made automatically")
        print("   - Close the window to stop monitoring")
        monitor.create_dashboard()
        
    elif choice == "2":
        print("\n📊 Current metrics:")
        monitor.print_current_metrics()
        
    elif choice == "3":
        print("\n🔄 Generating sample predictions...")
        for i in range(5):
            result = monitor.make_prediction()
            if result['success']:
                print(f"Prediction {i+1}: ${result['prediction']:.2f} "
                      f"(Response: {result['response_time']:.1f}ms)")
            time.sleep(1)
        
        print("\n📊 Updated metrics:")
        monitor.print_current_metrics()
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
