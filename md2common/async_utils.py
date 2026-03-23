"""
异步工具模块

提供异步/同步接口统一的工具函数和装饰器
"""

import asyncio
import concurrent.futures
import functools
from typing import Callable, TypeVar, Coroutine, Any

T = TypeVar('T')


def sync_wrapper(async_func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    将异步函数包装为同步函数的装饰器

    使用 ThreadPoolExecutor 在新线程中运行异步函数，
    避免事件循环冲突

    Args:
        async_func: 异步函数

    Returns:
        同步包装函数

    Example:
        @sync_wrapper
        async def my_async_func(x: int) -> int:
            await asyncio.sleep(1)
            return x * 2

        # 现在可以同步调用
        result = my_async_func(5)
    """
    @functools.wraps(async_func)
    def sync_wrapper_fn(*args: Any, **kwargs: Any) -> T:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, async_func(*args, **kwargs))
            return future.result()

    return sync_wrapper_fn


async def run_async_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    在异步上下文中运行同步函数

    Args:
        func: 同步函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数返回值

    Example:
        async def my_async_func():
            result = await run_async_sync(sync_blocking_func, arg1, arg2)
            return result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
