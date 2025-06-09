"""
Ticker configuration management for technical analysis
Loads and provides access to curated ticker lists from YAML configuration
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class TickerConfig:
    """Manages ticker configuration from YAML file"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize ticker configuration
        
        Args:
            config_file: Path to YAML config file. If None, uses default tickers.yaml
        """
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), 'tickers.yaml')
        
        self.config_file = config_file
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load ticker configuration from YAML file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Ticker configuration file not found: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all ticker categories with their descriptions and tickers"""
        return self._config.get('categories', {})
    
    def get_category(self, category_name: str) -> Dict[str, Any]:
        """
        Get specific ticker category
        
        Args:
            category_name: Name of the category (e.g., 'large_cap', 'technology')
            
        Returns:
            Category data including description and tickers
            
        Raises:
            KeyError: If category doesn't exist
        """
        categories = self.get_categories()
        if category_name not in categories:
            available = list(categories.keys())
            raise KeyError(f"Category '{category_name}' not found. Available: {available}")
        
        return categories[category_name]
    
    def get_category_tickers(self, category_name: str) -> List[Dict[str, Any]]:
        """
        Get ticker list for specific category
        
        Args:
            category_name: Name of the category
            
        Returns:
            List of ticker dictionaries with symbol, name, sector, etc.
        """
        category = self.get_category(category_name)
        return category.get('tickers', [])
    
    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """
        Get all tickers from all categories (deduplicated)
        
        Returns:
            List of unique ticker dictionaries
        """
        all_tickers = []
        seen_symbols = set()
        
        for category in self.get_categories().values():
            for ticker in category.get('tickers', []):
                symbol = ticker.get('symbol')
                if symbol and symbol not in seen_symbols:
                    all_tickers.append(ticker)
                    seen_symbols.add(symbol)
        
        return sorted(all_tickers, key=lambda x: x.get('symbol', ''))
    
    def search_tickers(self, query: str) -> List[Dict[str, Any]]:
        """
        Search tickers by symbol or company name
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching ticker dictionaries
        """
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        query_upper = query.upper()
        matches = []
        
        for ticker in self.get_all_tickers():
            symbol = ticker.get('symbol', '')
            name = ticker.get('name', '')
            
            if (query_upper in symbol or 
                query_lower in name.lower()):
                matches.append(ticker)
        
        return matches
    
    def get_ticker_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker information by symbol
        
        Args:
            symbol: Ticker symbol (case-insensitive)
            
        Returns:
            Ticker dictionary if found, None otherwise
        """
        symbol_upper = symbol.upper()
        
        for ticker in self.get_all_tickers():
            if ticker.get('symbol', '').upper() == symbol_upper:
                return ticker
        
        return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata"""
        return self._config.get('metadata', {})
    
    def get_strategy_recommendations(self) -> Dict[str, Any]:
        """Get strategy-specific ticker recommendations"""
        return self._config.get('strategy_recommendations', {})
    
    def get_recommended_tickers_for_strategy(self, strategy_type: str) -> List[str]:
        """
        Get recommended ticker categories for a strategy type
        
        Args:
            strategy_type: Type of strategy (e.g., 'trend_following', 'momentum')
            
        Returns:
            List of recommended category names
        """
        recommendations = self.get_strategy_recommendations()
        strategy_rec = recommendations.get(strategy_type, {})
        return strategy_rec.get('recommended_categories', [])
    
    def get_category_names(self) -> List[str]:
        """Get list of available category names"""
        return list(self.get_categories().keys())
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol exists in configuration
        
        Args:
            symbol: Ticker symbol to validate
            
        Returns:
            True if symbol exists in configuration
        """
        return self.get_ticker_by_symbol(symbol) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about ticker configuration"""
        categories = self.get_categories()
        total_tickers = len(self.get_all_tickers())
        
        category_stats = {}
        for cat_name, cat_data in categories.items():
            category_stats[cat_name] = {
                'count': len(cat_data.get('tickers', [])),
                'description': cat_data.get('description', '')
            }
        
        return {
            'total_categories': len(categories),
            'total_unique_tickers': total_tickers,
            'categories': category_stats,
            'metadata': self.get_metadata()
        }
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self._load_config()


# Global instance for easy import
ticker_config = TickerConfig()


def get_ticker_config() -> TickerConfig:
    """Get the global ticker configuration instance"""
    return ticker_config 