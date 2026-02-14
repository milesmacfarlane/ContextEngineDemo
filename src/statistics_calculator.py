"""
Statistics Calculator - Core calculation functions
Used by all statistics question generators
"""

import numpy as np
from typing import List, Union
from collections import Counter


class StatisticsCalculator:
    """Statistical calculation utilities"""
    
    @staticmethod
    def calculate_mean(data: List[Union[int, float]]) -> float:
        """Calculate arithmetic mean"""
        return np.mean(data)
    
    @staticmethod
    def calculate_median(data: List[Union[int, float]]) -> float:
        """Calculate median"""
        return np.median(data)
    
    @staticmethod
    def calculate_mode(data: List[Union[int, float]]) -> str:
        """
        Calculate mode, handling multiple modes and no mode
        
        Returns:
            "no mode" - if all values appear once
            "all values" - if all values appear the same number of times (>1)
            "8" - single mode
            "3, 8" - multiple modes
        """
        counts = Counter(data)
        max_count = max(counts.values())
        
        # No mode - all values appear once
        if max_count == 1:
            return "no mode"
        
        # Find all modes
        modes = [k for k, v in counts.items() if v == max_count]
        modes.sort()
        
        # All values are modes
        if len(modes) == len(set(data)):
            return "all values"
        
        # Single mode
        if len(modes) == 1:
            # Check if it's an integer
            if isinstance(modes[0], (int, np.integer)) or modes[0] == int(modes[0]):
                return str(int(modes[0]))
            return str(modes[0])
        
        # Multiple modes
        formatted_modes = []
        for m in modes:
            if isinstance(m, (int, np.integer)) or m == int(m):
                formatted_modes.append(str(int(m)))
            else:
                formatted_modes.append(str(m))
        return ", ".join(formatted_modes)
    
    @staticmethod
    def identify_outliers(data: List[Union[int, float]], 
                         method: str = "visual") -> List[Union[int, float]]:
        """
        Identify outliers in data
        
        For EMA40S, we use a "visual" method - values that are
        significantly different from the cluster
        """
        if len(data) < 4:
            return []
        
        sorted_data = sorted(data)
        
        # Simple method: values more than 2x IQR from Q1/Q3
        q1 = np.percentile(sorted_data, 25)
        q3 = np.percentile(sorted_data, 75)
        iqr = q3 - q1
        
        if iqr == 0:
            # Look for values very different from median
            median = np.median(sorted_data)
            std = np.std(sorted_data)
            if std == 0:
                return []
            outliers = [x for x in data if abs(x - median) > 2 * std]
            return outliers
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        return outliers
    
    @staticmethod
    def calculate_trimmed_mean(data: List[Union[int, float]], 
                              num_to_remove: int = 1) -> float:
        """
        Calculate trimmed mean by removing highest and lowest values
        
        Args:
            data: The dataset
            num_to_remove: Number to remove from each end (default: 1)
        """
        sorted_data = sorted(data)
        
        if len(sorted_data) <= 2 * num_to_remove:
            raise ValueError("Dataset too small to trim")
        
        trimmed = sorted_data[num_to_remove:-num_to_remove]
        return np.mean(trimmed)
    
    @staticmethod
    def calculate_weighted_mean(values: List[float], weights: List[float]) -> float:
        """
        Calculate weighted mean
        
        Args:
            values: The values
            weights: The weights (should sum to 1.0 or 100)
        
        Returns:
            Weighted mean
        """
        if len(values) != len(weights):
            raise ValueError("Values and weights must have same length")
        
        # Normalize weights if they don't sum to 1
        weight_sum = sum(weights)
        if weight_sum != 1.0:
            weights = [w / weight_sum for w in weights]
        
        return sum(v * w for v, w in zip(values, weights))
    
    @staticmethod
    def calculate_weighted_mean_frequency(values: List[float], 
                                         frequencies: List[int]) -> float:
        """
        Calculate weighted mean from frequency data
        
        Example: 
            values = [6, 8, 10, 12]
            frequencies = [2, 3, 3, 6]
            (2×6 + 3×8 + 3×10 + 6×12) / 14 = 9.86
        """
        if len(values) != len(frequencies):
            raise ValueError("Values and frequencies must have same length")
        
        total = sum(v * f for v, f in zip(values, frequencies))
        count = sum(frequencies)
        
        return total / count
    
    @staticmethod
    def percentile_rank(value: Union[int, float], 
                       dataset: List[Union[int, float]]) -> float:
        """
        Calculate percentile rank using formula: PR = (b/n) × 100
        
        Args:
            value: The value to find percentile rank for
            dataset: The complete dataset
        
        Returns:
            Percentile rank (0-99)
        """
        b = sum(1 for x in dataset if x < value)  # Count below
        n = len(dataset)  # Total count
        
        if n == 0:
            return 0.0
        
        return (b / n) * 100
    
    @staticmethod
    def value_at_percentile(percentile: float, 
                           dataset: List[Union[int, float]]) -> float:
        """
        Find value at given percentile
        
        Args:
            percentile: Percentile (0-100)
            dataset: The dataset
        
        Returns:
            Value at that percentile
        """
        return np.percentile(dataset, percentile)


# Test functions
if __name__ == "__main__":
    print("=== Testing Statistics Calculator ===\n")
    
    # Test data
    data1 = [7, 2, 4, 7, 0, 1, 3, 2, 6, 1]
    print(f"Dataset: {data1}")
    print(f"Mean: {StatisticsCalculator.calculate_mean(data1):.2f}")
    print(f"Median: {StatisticsCalculator.calculate_median(data1)}")
    print(f"Mode: {StatisticsCalculator.calculate_mode(data1)}")
    
    # Test with outliers
    data2 = [3, 9, 5, 8, 4, 6, 20]
    print(f"\nDataset with outlier: {data2}")
    print(f"Mean: {StatisticsCalculator.calculate_mean(data2):.2f}")
    outliers = StatisticsCalculator.identify_outliers(data2)
    print(f"Outliers: {outliers}")
    if outliers:
        print(f"Trimmed mean: {StatisticsCalculator.calculate_trimmed_mean(data2):.2f}")
    
    # Test weighted mean
    values = [85, 72, 65, 90]
    weights = [0.10, 0.20, 0.20, 0.50]
    print(f"\nWeighted mean test:")
    print(f"Values: {values}")
    print(f"Weights: {weights}")
    print(f"Weighted mean: {StatisticsCalculator.calculate_weighted_mean(values, weights):.2f}")
    
    # Test percentile rank
    data3 = [620, 655, 706, 722, 722, 768, 775, 778, 780, 784, 
             784, 800, 803, 816, 824, 824, 831, 840, 849, 852]
    print(f"\nPercentile rank for 800 in credit score dataset:")
    print(f"PR = {StatisticsCalculator.percentile_rank(800, data3):.0f}")
