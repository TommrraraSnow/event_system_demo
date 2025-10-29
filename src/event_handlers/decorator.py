from __future__ import annotations

from typing import Any, Callable, TypeVar, overload
from functools import wraps

from events.base import EventABC, EventContext
from event_types import EventType
from event_handlers.base import EventHandler
from event_handlers.registry import EventHandlerRegistry

T = TypeVar('T', bound=Callable[..., Any])

# 全局注册表实例
_global_registry: EventHandlerRegistry | None = None


def get_global_registry() -> EventHandlerRegistry:
    """获取全局事件处理器注册表实例。

    Returns:
        EventHandlerRegistry: 全局注册表实例

    Raises:
        RuntimeError: 如果全局注册表未初始化
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = EventHandlerRegistry()
    return _global_registry


@overload
def event_handler(event_type: EventType) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

@overload
def event_handler(event_type: EventType) -> Callable[[T], T]: ...


def event_handler(event_type: EventType) -> Callable[[T], T]:
    """事件处理器装饰器，用于自动注册处理器到全局注册表。

    Args:
        event_type: 要处理的事件类型

    Returns:
        装饰器函数

    Example:
        @event_handler(EventTypes.PLAYER_CREATED)
        def handle_player_created(event: Event, context: EventContext) -> Iterable[Event]:
            print(f"Player created: {event.event_message.payload}")
            return []
    """
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # 创建处理器类
        class FunctionEventHandler(EventHandler):
            def __init__(self, handler_func: Callable[..., Any]):
                self._handler_func = handler_func
                self._event_type = event_type

            def supports(self, event: EventABC) -> bool:
                return event.event_type == self._event_type

            def handle(self, event: EventABC, context: EventContext) -> list[EventABC]:
                return list(self._handler_func(event, context))

            def __repr__(self) -> str:
                return f"FunctionEventHandler({self._event_type}, {self._handler_func.__name__})"

        # 注册到全局注册表
        registry = get_global_registry()
        handler_instance = FunctionEventHandler(func)
        registry.register(event_type, handler_instance)

        # 将处理器实例附加到函数上，以便后续访问
        setattr(wrapper, '_event_handler', handler_instance)
        setattr(wrapper, '_event_type', event_type)

        return wrapper  # type: ignore

    return decorator


class auto_register:
    """类装饰器，用于自动注册 EventHandler 子类到全局注册表。

    Args:
        event_type: 要处理的事件类型

    Example:
        @auto_register(EventTypes.PLAYER_HEALTH_CHANGED)
        class HealthLogger(EventHandler):
            def supports(self, event):
                return event.event_type == EventTypes.PLAYER_HEALTH_CHANGED

            def handle(self, event, context):
                print(f"Health changed: {event.event_message.payload}")
                return []
    """
    def __init__(self, event_type: EventType):
        self.event_type = event_type

    def __call__(self, cls: type[T]) -> type[T]:
        # 确保类继承自 EventHandler
        if not issubclass(cls, EventHandler):
            raise TypeError(f"装饰的类 {cls.__name__} 必须继承自 EventHandler")

        # 创建实例并注册
        handler_instance = cls()
        registry = get_global_registry()
        registry.register(self.event_type, handler_instance)

        # 在类上标记注册信息
        setattr(cls, '_registered_event_type', self.event_type)
        setattr(cls, '_is_auto_registered', True)

        return cls


def register_handler(event_type: EventType, handler: EventHandler) -> None:
    """手动注册事件处理器到全局注册表。

    Args:
        event_type: 事件类型
        handler: 事件处理器实例
    """
    registry = get_global_registry()
    registry.register(event_type, handler)


def clear_registry() -> None:
    """清空全局注册表。主要用于测试。"""
    global _global_registry
    _global_registry = None