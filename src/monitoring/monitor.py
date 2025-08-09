"""
Monitoring and logging utilities for the ML service.
"""

import logging
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os


class ModelMonitor:
    """Monitor model performance and predictions."""
    
    def __init__(self, db_path="logs/predictions.db"):
        self.db_path = db_path
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/model_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_prediction_stats(self, days=7) -> Dict[str, Any]:
        """Get prediction statistics for the last N days."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Calculate date threshold
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Query predictions
            query = """
                SELECT * FROM predictions 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """
            
            df = pd.read_sql_query(query, conn, params=[date_threshold])
            conn.close()
            
            if df.empty:
                return {"message": "No predictions found", "count": 0}
            
            stats = {
                "total_predictions": len(df),
                "date_range": {
                    "start": df['timestamp'].min(),
                    "end": df['timestamp'].max()
                },
                "prediction_stats": {
                    "mean": float(df['prediction'].mean()),
                    "median": float(df['prediction'].median()),
                    "std": float(df['prediction'].std()),
                    "min": float(df['prediction'].min()),
                    "max": float(df['prediction'].max())
                },
                "predictions_per_day": df.groupby(
                    df['timestamp'].str[:10]
                ).size().to_dict()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting prediction stats: {e}")
            return {"error": str(e)}
    
    def check_data_drift(self) -> Dict[str, Any]:
        """Check for potential data drift in recent predictions."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent and older predictions
            recent_query = """
                SELECT * FROM predictions 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            """
            
            older_query = """
                SELECT * FROM predictions 
                WHERE timestamp < ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            """
            
            recent_threshold = (datetime.now() - timedelta(days=7)).isoformat()
            older_threshold = (datetime.now() - timedelta(days=14)).isoformat()
            
            recent_df = pd.read_sql_query(recent_query, conn, params=[recent_threshold])
            older_df = pd.read_sql_query(older_query, conn, params=[older_threshold])
            
            conn.close()
            
            if recent_df.empty or older_df.empty:
                return {"message": "Insufficient data for drift detection"}
            
            # Compare prediction distributions
            recent_mean = recent_df['prediction'].mean()
            older_mean = older_df['prediction'].mean()
            
            drift_score = abs(recent_mean - older_mean) / older_mean if older_mean != 0 else 0
            
            return {
                "drift_detected": drift_score > 0.1,  # 10% threshold
                "drift_score": float(drift_score),
                "recent_mean": float(recent_mean),
                "older_mean": float(older_mean),
                "threshold": 0.1
            }
            
        except Exception as e:
            self.logger.error(f"Error checking data drift: {e}")
            return {"error": str(e)}
    
    def get_model_health(self) -> Dict[str, Any]:
        """Get overall model health status."""
        try:
            # Get recent prediction stats
            stats = self.get_prediction_stats(days=1)
            drift_info = self.check_data_drift()
            
            # Determine health status
            health_score = 100
            issues = []
            
            # Check prediction volume
            if stats.get("total_predictions", 0) == 0:
                health_score -= 30
                issues.append("No recent predictions")
            elif stats.get("total_predictions", 0) < 10:
                health_score -= 10
                issues.append("Low prediction volume")
            
            # Check for drift
            if drift_info.get("drift_detected", False):
                health_score -= 20
                issues.append("Data drift detected")
            
            # Determine status
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "health_score": health_score,
                "issues": issues,
                "last_check": datetime.now().isoformat(),
                "recent_stats": stats,
                "drift_info": drift_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model health: {e}")
            return {"status": "error", "error": str(e)}
    
    def export_logs(self, format="json", days=30) -> str:
        """Export prediction logs."""
        try:
            conn = sqlite3.connect(self.db_path)
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT * FROM predictions 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """
            
            df = pd.read_sql_query(query, conn, params=[date_threshold])
            conn.close()
            
            if df.empty:
                return "No data to export"
            
            # Create export directory
            os.makedirs("exports", exist_ok=True)
            
            # Export based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "csv":
                filename = f"exports/predictions_{timestamp}.csv"
                df.to_csv(filename, index=False)
            else:  # JSON
                filename = f"exports/predictions_{timestamp}.json"
                df.to_json(filename, orient="records", indent=2)
            
            self.logger.info(f"Logs exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            return f"Export failed: {e}"


def main():
    """Example usage of monitor."""
    monitor = ModelMonitor()
    
    print("Model Health Status:")
    health = monitor.get_model_health()
    print(json.dumps(health, indent=2))
    
    print("\nPrediction Statistics:")
    stats = monitor.get_prediction_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
