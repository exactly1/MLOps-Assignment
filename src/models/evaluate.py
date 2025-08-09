"""
Model evaluation and visualization utilities.
"""

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import json
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.data_processor import DataProcessor


class ModelEvaluator:
    """Evaluate and visualize model performance."""
    
    def __init__(self, models_dir="models", plots_dir="plots"):
        self.models_dir = models_dir
        self.plots_dir = plots_dir
        os.makedirs(plots_dir, exist_ok=True)
    
    def load_models(self):
        """Load all trained models."""
        models = {}
        model_files = {
            'linear_regression': 'linear_regression.joblib',
            'random_forest': 'random_forest.joblib',
            'gradient_boosting': 'gradient_boosting.joblib'
        }
        
        for name, filename in model_files.items():
            filepath = os.path.join(self.models_dir, filename)
            if os.path.exists(filepath):
                models[name] = joblib.load(filepath)
        
        return models
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate a single model."""
        y_pred = model.predict(X_test)
        
        return {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred),
            'predictions': y_pred
        }
    
    def compare_models(self):
        """Compare all models and generate evaluation report."""
        # Load data
        processor = DataProcessor()
        data = processor.prepare_data()
        
        # Load models
        models = self.load_models()
        
        if not models:
            print("No models found to evaluate!")
            return
        
        # Evaluate each model
        results = {}
        for name, model in models.items():
            print(f"Evaluating {name}...")
            results[name] = self.evaluate_model(model, data['X_test'], data['y_test'])
        
        # Create comparison plots
        self.plot_model_comparison(results)
        self.plot_predictions_vs_actual(results, data['y_test'])
        
        # Save evaluation metrics
        metrics = {
            name: {
                'rmse': float(result['rmse']),
                'mae': float(result['mae']),
                'r2_score': float(result['r2_score'])
            }
            for name, result in results.items()
        }
        
        with open('evaluation_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return results
    
    def plot_model_comparison(self, results):
        """Plot model comparison metrics."""
        metrics = ['rmse', 'mae', 'r2_score']
        model_names = list(results.keys())
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, metric in enumerate(metrics):
            values = [results[name][metric] for name in model_names]
            axes[i].bar(model_names, values)
            axes[i].set_title(f'{metric.upper()}')
            axes[i].set_ylabel(metric.upper())
            
            # Rotate x-axis labels for better readability
            axes[i].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'model_comparison.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_predictions_vs_actual(self, results, y_test):
        """Plot predictions vs actual values for all models."""
        n_models = len(results)
        fig, axes = plt.subplots(1, n_models, figsize=(5*n_models, 5))
        
        if n_models == 1:
            axes = [axes]
        
        for i, (name, result) in enumerate(results.items()):
            y_pred = result['predictions']
            
            axes[i].scatter(y_test, y_pred, alpha=0.6)
            axes[i].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            axes[i].set_xlabel('Actual Values')
            axes[i].set_ylabel('Predicted Values')
            axes[i].set_title(f'{name}\nR² = {result["r2_score"]:.3f}')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'predictions_vs_actual.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self):
        """Plot feature importance for tree-based models."""
        models = self.load_models()
        processor = DataProcessor()
        data = processor.prepare_data()
        feature_names = data['feature_names']
        
        # Focus on tree-based models that have feature importance
        tree_models = {k: v for k, v in models.items() 
                      if hasattr(v, 'feature_importances_')}
        
        if not tree_models:
            print("No tree-based models found for feature importance analysis")
            return
        
        n_models = len(tree_models)
        fig, axes = plt.subplots(1, n_models, figsize=(8*n_models, 6))
        
        if n_models == 1:
            axes = [axes]
        
        for i, (name, model) in enumerate(tree_models.items()):
            importance = model.feature_importances_
            
            # Sort features by importance
            indices = np.argsort(importance)[::-1]
            
            axes[i].bar(range(len(importance)), importance[indices])
            axes[i].set_title(f'Feature Importance - {name}')
            axes[i].set_xlabel('Features')
            axes[i].set_ylabel('Importance')
            axes[i].set_xticks(range(len(importance)))
            axes[i].set_xticklabels([feature_names[i] for i in indices], rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'feature_importance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self):
        """Generate a comprehensive evaluation report."""
        print("Generating model evaluation report...")
        
        # Run evaluation
        results = self.compare_models()
        self.plot_feature_importance()
        
        # Print summary
        print("\n" + "="*60)
        print("MODEL EVALUATION SUMMARY")
        print("="*60)
        
        for name, result in results.items():
            print(f"\n{name.upper()}:")
            print(f"  RMSE: {result['rmse']:.4f}")
            print(f"  MAE:  {result['mae']:.4f}")
            print(f"  R²:   {result['r2_score']:.4f}")
        
        # Find best model
        best_model = min(results.items(), key=lambda x: x[1]['rmse'])
        print(f"\nBEST MODEL: {best_model[0]} (RMSE: {best_model[1]['rmse']:.4f})")
        print("="*60)
        
        return results


def main():
    """Main evaluation script."""
    evaluator = ModelEvaluator()
    evaluator.generate_report()


if __name__ == "__main__":
    main()
