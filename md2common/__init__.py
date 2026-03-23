"""
md2common - Markdown转换工具共享模块

提供md2pdf和md2docx模块共享的工具函数和类
"""

from .async_utils import sync_wrapper, run_async_sync

__all__ = [
    'sync_wrapper',
    'run_async_sync',
]
