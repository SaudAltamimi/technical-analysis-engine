"""
Configuration models for technical analysis strategies
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

try:
    from .ta_types import IndicatorType, SignalType, CrossoverDirection, ThresholdCondition
except ImportError:
    from ta_types import IndicatorType, SignalType, CrossoverDirection, ThresholdCondition


class IndicatorParams(BaseModel):
    """Base parameters for all indicators"""
    
    class Config:
        extra = "forbid"  # Strict validation - no extra fields allowed


class EMAConfig(IndicatorParams):
    """EMA indicator configuration"""
    window: int = Field(20, ge=2, le=200, description="EMA period")


class SMAConfig(IndicatorParams):
    """SMA indicator configuration"""
    window: int = Field(20, ge=2, le=200, description="SMA period")


class RSIConfig(IndicatorParams):
    """RSI indicator configuration"""
    window: int = Field(14, ge=2, le=100, description="RSI period")


class MACDConfig(IndicatorParams):
    """MACD indicator configuration"""
    fast: int = Field(12, ge=2, le=50, description="Fast EMA period")
    slow: int = Field(26, ge=2, le=100, description="Slow EMA period") 
    signal: int = Field(9, ge=2, le=50, description="Signal line period")
    
    @model_validator(mode='after')
    def validate_periods(self):
        """Validate that slow period is greater than fast period"""
        if self.slow <= self.fast:
            raise ValueError(f"Slow period ({self.slow}) must be greater than fast period ({self.fast})")
        return self


class IndicatorDefinition(BaseModel):
    """Complete indicator definition"""
    name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$', description="Indicator name")
    type: IndicatorType = Field(..., description="Indicator type")
    params: IndicatorParams = Field(..., description="Indicator parameters")


class CrossoverRule(BaseModel):
    """Crossover-based trading rule"""
    name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    fast_indicator: str = Field(..., description="Indicator that crosses")
    slow_indicator: str = Field(..., description="Indicator being crossed")
    direction: CrossoverDirection = Field(..., description="Crossover direction")
    signal_type: SignalType = Field(..., description="Signal type")


class ThresholdRule(BaseModel):
    """Threshold-based trading rule"""
    name: str = Field(..., pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    indicator: str = Field(..., description="Target indicator")
    threshold: float = Field(..., description="Threshold value")
    condition: ThresholdCondition = Field(..., description="Comparison condition")
    signal_type: SignalType = Field(..., description="Signal type")


class StrategyDefinition(BaseModel):
    """Complete strategy definition"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    indicators: List[IndicatorDefinition] = Field(..., min_items=1)
    crossover_rules: List[CrossoverRule] = Field(default_factory=list)
    threshold_rules: List[ThresholdRule] = Field(default_factory=list)
    
    @field_validator('indicators')
    @classmethod
    def unique_indicator_names(cls, indicators):
        names = [ind.name for ind in indicators]
        if len(names) != len(set(names)):
            raise ValueError("Indicator names must be unique")
        return indicators
    
    @model_validator(mode='after')
    def validate_rule_references(self):
        """Ensure all rules reference existing indicators"""
        indicator_names = {ind.name for ind in self.indicators}
        
        # Validate crossover rules
        for rule in self.crossover_rules:
            if rule.fast_indicator not in indicator_names:
                raise ValueError(f"Unknown indicator: {rule.fast_indicator}")
            if rule.slow_indicator not in indicator_names:
                raise ValueError(f"Unknown indicator: {rule.slow_indicator}")
        
        # Validate threshold rules  
        for rule in self.threshold_rules:
            if rule.indicator not in indicator_names:
                raise ValueError(f"Unknown indicator: {rule.indicator}")
        
        return self 