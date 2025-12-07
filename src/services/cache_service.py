from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    def __init__(self, cache_dir: Path = Path("cache")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(hours=1)
    
    def _get_cache_key(self, prefix: str, key: str) -> str:
        return f"{prefix}:{key}"
    
    def _get_cache_file(self, cache_key: str) -> Path:
        safe_key = cache_key.replace(":", "_").replace("/", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, prefix: str, key: str) -> Optional[Any]:
        cache_key = self._get_cache_key(prefix, key)
        
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if datetime.now() < entry["expires_at"]:
                logger.debug(f"Cache hit (memory): {cache_key}")
                return entry["data"]
            else:
                del self.memory_cache[cache_key]
        
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    expires_at = datetime.fromisoformat(entry["expires_at"])
                    if datetime.now() < expires_at:
                        logger.debug(f"Cache hit (file): {cache_key}")
                        return entry["data"]
                    else:
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Błąd odczytu cache: {e}")
        
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def set(self, prefix: str, key: str, data: Any, ttl: Optional[timedelta] = None) -> None:
        cache_key = self._get_cache_key(prefix, key)
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + ttl
        
        self.memory_cache[cache_key] = {
            "data": data,
            "expires_at": expires_at
        }
        
        cache_file = self._get_cache_file(cache_key)
        try:
            entry = {
                "data": data,
                "expires_at": expires_at.isoformat()
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, default=str)
            logger.debug(f"Cache set: {cache_key}")
        except Exception as e:
            logger.warning(f"Błąd zapisu cache: {e}")
    
    def delete(self, prefix: str, key: str) -> None:
        cache_key = self._get_cache_key(prefix, key)
        
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            cache_file.unlink()
        
        logger.debug(f"Cache deleted: {cache_key}")
    
    def clear(self, prefix: Optional[str] = None) -> None:
        if prefix:
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{prefix}:")]
            for key in keys_to_delete:
                del self.memory_cache[key]
            
            for cache_file in self.cache_dir.glob(f"{prefix.replace(':', '_')}_*.json"):
                cache_file.unlink()
        else:
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        
        logger.info(f"Cache cleared: {prefix or 'all'}")

