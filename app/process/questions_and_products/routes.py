from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import create_model
# from .schemas import Input
from .main import *
import inspect
import sys

internal_router = APIRouter()

def process_obj(obj):
    # Get parameters of the 'process' method, excluding 'self'
    process_params = inspect.signature(obj.process).parameters
    input_fields = {
        param_name: (param.annotation, ...)
        for param_name, param in process_params.items()
        if param_name != 'self'
    }
    InputModel = create_model(f"{obj.__name__}Input", **input_fields)

    # Get the return type of the 'process' method
    process_return_type = inspect.signature(obj.process).return_annotation
    if process_return_type is inspect.Signature.empty:
        process_return_type = dict

    # Dynamically generate the route function
    @internal_router.post(f"/{obj.__name__.lower()}/", response_model=process_return_type)
    async def route_func(input_data: InputModel = Depends()): # type: ignore
        instance = obj()
        try:
            result = await instance.process(**input_data.dict())
            return result  # Return the successful result
        except HTTPException as e:
            raise e  # Re-raise existing HTTPExceptions (e.g., 404, 422)
        except Exception as e:
            # Log the exception for debugging (optional)
            print(f"Error in {obj.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") 

    # Dynamically assign the route function name
    route_func.__name__ = obj.__name__.lower()
    globals()[route_func.__name__] = route_func

# Dynamically create routes for classes and modules
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and hasattr(obj, 'process'):
        process_obj(obj)
    elif inspect.ismodule(obj):  # Handle modules
        for inner_name, inner_obj in inspect.getmembers(obj):
            if inspect.isclass(inner_obj) and hasattr(inner_obj, 'process'):
                process_obj(inner_obj)