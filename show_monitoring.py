"""
Simple monitoring demo showing Prometheus metrics capabilities
"""

import json
import time
from datetime import datetime

def print_monitoring_dashboard():
    """Display monitoring dashboard information"""
    
    print("\n" + "🔍 " + "="*60)
    print("   PROMETHEUS MONITORING DASHBOARD DEMONSTRATION")
    print("="*70)
    
    print("\n📊 **Available Metrics in the ML API:**")
    print("   ✅ predictions_total - Total number of predictions made")
    print("   ✅ prediction_duration_seconds - Time spent on predictions")
    print("   ✅ http_requests_total - Total HTTP requests")
    print("   ✅ http_request_duration_seconds - HTTP request duration")
    print("   ✅ process_cpu_seconds_total - CPU usage")
    print("   ✅ process_memory_bytes - Memory usage")
    
    print("\n🎯 **Key Monitoring Features Implemented:**")
    
    print("\n1. **Real-time Metrics Collection:**")
    print("   • Counter: tracks total predictions")
    print("   • Histogram: measures prediction response times")  
    print("   • Gauge: monitors system resources")
    
    print("\n2. **API Endpoint Integration:**")
    print("   • GET /metrics - Prometheus metrics endpoint")
    print("   • Automatic metric collection on each prediction")
    print("   • Performance timing for all requests")
    
    print("\n3. **Sample Prometheus Metrics Output:**")
    print("   ```")
    print("   # HELP predictions_total Total number of predictions made")
    print("   # TYPE predictions_total counter") 
    print("   predictions_total 42.0")
    print("   ")
    print("   # HELP prediction_duration_seconds Time spent on predictions")
    print("   # TYPE prediction_duration_seconds histogram")
    print("   prediction_duration_seconds_bucket{le=\"0.005\"} 15.0")
    print("   prediction_duration_seconds_bucket{le=\"0.01\"} 25.0")
    print("   prediction_duration_seconds_bucket{le=\"0.025\"} 35.0")
    print("   prediction_duration_seconds_bucket{le=\"+Inf\"} 42.0")
    print("   prediction_duration_seconds_sum 0.8234")
    print("   prediction_duration_seconds_count 42.0")
    print("   ```")
    
    print("\n4. **Dashboard Capabilities:**")
    print("   • Real-time prediction volume tracking")
    print("   • Response time distribution analysis")
    print("   • Model performance monitoring")
    print("   • System resource utilization")
    print("   • Error rate tracking")
    
    print("\n5. **Integration with Grafana:**")
    print("   • Pre-configured dashboard templates")
    print("   • Alerting rules for performance thresholds")
    print("   • Historical trend analysis")
    print("   • Custom metric visualizations")
    
    print("\n📈 **Monitoring Architecture:**")
    print("   ```")
    print("   [ML API] --> [Prometheus Metrics] --> [Prometheus Server]")
    print("      |              |                       |")
    print("   [FastAPI]    [/metrics endpoint]    [Time Series DB]")
    print("      |              |                       |")
    print("   [Pydantic]   [Counter/Histogram]     [Grafana Dashboard]")
    print("   ```")
    
    print("\n🔧 **Setup Instructions:**")
    print("   1. Start API: python run_api.py")
    print("   2. View metrics: http://localhost:8000/metrics")
    print("   3. Start Prometheus: docker-compose up prometheus")
    print("   4. Start Grafana: docker-compose up grafana")
    print("   5. Access dashboard: http://localhost:3000")
    
    print("\n📋 **Sample Prometheus Configuration (prometheus.yml):**")
    print("   ```yaml")
    print("   scrape_configs:")
    print("     - job_name: 'ml-api'")
    print("       static_configs:")
    print("         - targets: ['ml-api:8000']")
    print("       metrics_path: '/metrics'")
    print("       scrape_interval: 5s")
    print("   ```")
    
    print("\n🎨 **Grafana Dashboard Panels:**")
    print("   • 📊 Total Predictions (Counter)")
    print("   • ⏱️  Average Response Time (Gauge)")
    print("   • 📈 Predictions per Minute (Rate)")
    print("   • 🎯 95th Percentile Response Time")
    print("   • 💻 CPU and Memory Usage")
    print("   • ❌ Error Rate Percentage")
    
    print("\n🚨 **Alerting Rules:**")
    print("   • High response time (>500ms)")
    print("   • Error rate above 5%")
    print("   • Memory usage above 80%")
    print("   • Prediction volume anomalies")
    
    print("\n📊 **Simulated Live Metrics (Example):**")
    
    # Simulate some live metrics
    for i in range(5):
        current_time = datetime.now().strftime("%H:%M:%S")
        predictions = 45 + i * 3
        avg_response = 120 + (i * 15)
        error_rate = 0.5 + (i * 0.2)
        
        print(f"   [{current_time}] Predictions: {predictions:3d} | "
              f"Avg Response: {avg_response:3d}ms | "
              f"Error Rate: {error_rate:.1f}% | "
              f"Status: {'🟢' if error_rate < 2 else '🟡'}")
        
        if i < 4:  # Don't sleep on last iteration
            time.sleep(1)
    
    print("\n🎯 **Benefits of This Monitoring Setup:**")
    print("   ✅ Production-ready observability")
    print("   ✅ Real-time performance insights")
    print("   ✅ Proactive issue detection")
    print("   ✅ Historical trend analysis")
    print("   ✅ Scalable monitoring architecture")
    print("   ✅ Industry-standard tooling")
    
    print("\n🔗 **Integration Points:**")
    print("   • MLflow: Model performance tracking")
    print("   • Docker: Containerized monitoring stack")
    print("   • CI/CD: Automated monitoring deployment")
    print("   • Logging: Centralized log aggregation")
    
    print("\n" + "="*70)
    print("   ✨ MONITORING DASHBOARD DEMONSTRATION COMPLETE ✨")
    print("="*70)

def show_docker_monitoring_setup():
    """Show Docker-based monitoring setup"""
    
    print("\n🐳 **Docker Compose Monitoring Stack:**")
    print("\n   The docker-compose.yml includes:")
    print("   • ml-api: Main ML service with metrics")
    print("   • prometheus: Metrics collection server")
    print("   • grafana: Dashboard and visualization")
    print("   • mlflow: Experiment tracking")
    
    print("\n   To start full monitoring stack:")
    print("   ```bash")
    print("   docker-compose up --build")
    print("   ```")
    
    print("\n   Access points:")
    print("   • API: http://localhost:8000")
    print("   • Metrics: http://localhost:8000/metrics")
    print("   • Prometheus: http://localhost:9090")
    print("   • Grafana: http://localhost:3000 (admin/admin)")
    print("   • MLflow: http://localhost:5000")

def main():
    """Main demonstration function"""
    print("🎬 **PROMETHEUS MONITORING DASHBOARD DEMO**")
    print("   This demonstrates the monitoring capabilities")
    print("   implemented in the MLOps Assignment")
    
    # Main dashboard demo
    print_monitoring_dashboard()
    
    # Docker setup info
    show_docker_monitoring_setup()
    
    print(f"\n⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 **Monitoring implementation showcases production-ready observability!**")

if __name__ == "__main__":
    main()
