"""
Technical indicator implementations and factory
"""

import pandas as pd
import vectorbt as vbt
from typing import Dict, Any, Protocol
from dataclasses import dataclass

try:
    from .ta_types import IndicatorType
    from .config import IndicatorDefinition, EMAConfig, SMAConfig, RSIConfig, MACDConfig
except ImportError:
    from ta_types import IndicatorType
    from config import IndicatorDefinition, EMAConfig, SMAConfig, RSIConfig, MACDConfig


class IndicatorProtocol(Protocol):
    """Protocol defining indicator interface
    
    A Protocol is a special class that defines an interface without implementation.
    It's used for structural typing - any class that implements the methods defined
    in the protocol will be considered compatible, even without explicit inheritance.
    
    In this case, any class that implements a calculate() method taking a pandas Series
    and returning a pandas Series will be considered an Indicator.
    
    Example:
        class MyIndicator:
            def calculate(self, data: pd.Series) -> pd.Series:
                return data * 2  # Some calculation
                
        # MyIndicator is compatible with IndicatorProtocol without explicit inheritance
    """
    
    def calculate(self, data: pd.Series) -> pd.Series:
        """Calculate indicator values
        
        Args:
            data: Input price/time series data
            
        Returns:
            Calculated indicator values as a pandas Series
        """
        ...


@dataclass(frozen=True)
class CalculatedIndicator:
    """Immutable result of indicator calculation
    
    The frozen=True parameter makes this dataclass immutable, meaning:
    - All attributes are read-only after initialization
    - Attempting to modify any attribute will raise FrozenInstanceError
    - This ensures data integrity and thread safety
    - Useful for representing final calculation results that shouldn't change
    """
    name: str
    values: pd.Series
    params: Dict[str, Any]


class IndicatorFactory:
    """Factory for creating and calculating indicators"""
    
    @staticmethod
    def create_ema(config: EMAConfig) -> IndicatorProtocol:
        """Create EMA indicator"""
        class EMA:
            def __init__(self, window: int):
                self.window = window
            
            def calculate(self, data: pd.Series) -> pd.Series:
                return vbt.MA.run(data, self.window, ewm=True).ma
        
        return EMA(config.window)
    
    @staticmethod
    def create_sma(config: SMAConfig) -> IndicatorProtocol:
        """Create SMA indicator"""
        class SMA:
            def __init__(self, window: int):
                self.window = window
            
            def calculate(self, data: pd.Series) -> pd.Series:
                return vbt.MA.run(data, self.window, ewm=False).ma
        
        return SMA(config.window)
    
    @staticmethod 
    def create_rsi(config: RSIConfig) -> IndicatorProtocol:
        """Create RSI indicator"""
        class RSI:
            def __init__(self, window: int):
                self.window = window
            
            def calculate(self, data: pd.Series) -> pd.Series:
                return vbt.RSI.run(data, self.window).rsi
        
        return RSI(config.window)
    
    @staticmethod
    def create_macd(config: MACDConfig) -> IndicatorProtocol:
        """Create MACD indicator"""
        class MACD:
            def __init__(self, fast: int, slow: int, signal: int):
                self.fast = fast
                self.slow = slow
                self.signal = signal
            
            def calculate(self, data: pd.Series) -> pd.Series:
                return vbt.MACD.run(
                    data, 
                    fast_window=self.fast,
                    slow_window=self.slow, 
                    signal_window=self.signal
                ).macd
        
        return MACD(config.fast, config.slow, config.signal)
    
    @classmethod
    def create_indicator(cls, definition: IndicatorDefinition) -> IndicatorProtocol:
        """Create indicator from definition"""
        creators = {
            IndicatorType.EMA: cls.create_ema,
            IndicatorType.SMA: cls.create_sma,
            IndicatorType.RSI: cls.create_rsi, 
            IndicatorType.MACD: cls.create_macd,
        }
        
        creator = creators.get(definition.type)
        if not creator:
            raise ValueError(f"Unsupported indicator type: {definition.type}")
        
        return creator(definition.params) 