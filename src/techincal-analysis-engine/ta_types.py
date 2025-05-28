"""
Core types and enums for the technical analysis framework
"""

from enum import Enum


class IndicatorType(str, Enum):
    """Supported technical indicators"""
    EMA = "EMA"
    SMA = "SMA" 
    RSI = "RSI"
    MACD = "MACD"


class SignalType(str, Enum):
    """Types of trading signals"""
    ENTRY = "entry"
    EXIT = "exit"


class CrossoverDirection(str, Enum):
    """Direction of crossover"""
    ABOVE = "above"
    BELOW = "below"


class ThresholdCondition(str, Enum):
    """Threshold comparison conditions"""
    ABOVE = "above"
    BELOW = "below" 