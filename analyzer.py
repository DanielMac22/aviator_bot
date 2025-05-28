import numpy as np
from typing import List

class AviatorAnalyzer:
    @staticmethod
    def analyze(history: List[float]) -> str:
        """Analyze historical data and make prediction"""
        if len(history) < 100:
            return "Insufficient data for prediction"
        
        recent = history[-100:]
        
        # Calculate statistical features
        mean = np.mean(recent)
        std_dev = np.std(recent)
        crash_rate = len([x for x in recent if x < 1.5]) / len(recent)
        
        # Pattern detection
        if crash_rate > 0.8:
            return self._predict_crash_streak(recent)
        elif std_dev > 2.0:
            return self._predict_volatile(recent)
        else:
            return self._predict_normal(recent)
    
    @staticmethod
    def _predict_crash_streak(data: List[float]) -> str:
        """Predict during crash streaks"""
        return f"1.10x-1.30x (Crash streak detected)"
    
    @staticmethod
    def _predict_volatile(data: List[float]) -> str:
        """Predict during volatile periods"""
        last_high = max(data[-10:])
        prediction = min(2.0, last_high * 0.7)
        return f"{prediction:.2f}x (Volatile market)"
    
    @staticmethod
    def _predict_normal(data: List[float]) -> str:
        """Standard prediction"""
        weighted_avg = sum(x * 0.9**i for i, x in enumerate(reversed(data[-20:])))
        norm_factor = sum(0.9**i for i in range(20))
        prediction = max(1.2, weighted_avg / norm_factor)
        return f"{prediction:.2f}x (Normal market)"
