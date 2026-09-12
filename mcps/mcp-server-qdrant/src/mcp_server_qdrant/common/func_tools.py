import inspect
from typing import Callable, get_type_hints


def make_partial_function(original_func: Callable, fixed_values: dict) -> Callable:
    sig = inspect.signature(original_func)
    remaining_params = [name for name in sig.parameters if name not in fixed_values]

    def bind_arguments(args, kwargs):
        bound_args = dict(fixed_values)
        for name, value in zip(remaining_params, args):
            bound_args[name] = value
        bound_args.update(kwargs)
        return bound_args

    if inspect.iscoroutinefunction(original_func):
        async def wrapper(*args, **kwargs):
            return await original_func(**bind_arguments(args, kwargs))
    else:
        def wrapper(*args, **kwargs):
            return original_func(**bind_arguments(args, kwargs))

    # Only keep parameters NOT in fixed_values
    new_params = [sig.parameters[name] for name in remaining_params]

    # FastMCP/Pydantic inspect both signature and annotations. Keep them aligned.
    wrapper.__signature__ = sig.replace(parameters=new_params)  # type:ignore
    wrapper.__name__ = original_func.__name__
    wrapper.__qualname__ = original_func.__qualname__
    wrapper.__doc__ = original_func.__doc__
    type_hints = get_type_hints(original_func)
    wrapper.__annotations__ = {
        name: type_hints[name] for name in remaining_params if name in type_hints
    }
    if "return" in type_hints:
        wrapper.__annotations__["return"] = type_hints["return"]

    return wrapper
