from abc import ABC
from langchain.tools import BaseTool
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class BaseHRTool(BaseTool, ABC):
    """Base class for all HR hiring tools."""
    
    def _handle_error(self, error: Exception) -> str:
        """Handle errors in tool execution."""
        error_msg = f"Error in {self.name}: {str(error)}"
        logger.error(error_msg)
        return error_msg
    
    def _run(self, *args, **kwargs) -> str:
        """Wrapper for synchronous tool execution with error handling."""
        try:
            return self._execute(*args, **kwargs)
        except Exception as e:
            return self._handle_error(e)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Wrapper for asynchronous tool execution with error handling."""
        try:
            return await self._aexecute(*args, **kwargs)
        except Exception as e:
            return self._handle_error(e)
    
    def _execute(self, *args, **kwargs) -> str:
        """Override this method for synchronous execution logic."""
        raise NotImplementedError("Synchronous execution not implemented")
    
    async def _aexecute(self, *args, **kwargs) -> str:
        """Override this method for asynchronous execution logic."""
        # Default to synchronous execution
        return self._execute(*args, **kwargs)