from typing import Union
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import io


class APIResponse:
    @staticmethod
    def success(data: Union[dict, None] = None, message: str = "Success", status_code: int = 200):
        return JSONResponse(content={"status": "success", "message": message, "data": data, "status_code": status_code},
                            status_code=status_code)

    @staticmethod
    def failure(data: Union[dict, None] = None, message: str = "Failed", status_code: int = 400):
        return JSONResponse(content={"status": "failure", "message": message, "data": data, "status_code": status_code},
                            status_code=status_code)

    @staticmethod
    def redirection(data: Union[dict, None] = None, message: str = "Redirected", status_code: int = 301):
        return JSONResponse(
            content={"status": "redirection", "message": message, "data": data, "status_code": status_code},
            status_code=status_code)

    @staticmethod
    def unauthorized(data: Union[dict, None] = None, message: str = "Unauthorized", status_code: int = 401):
        return JSONResponse(
            content={"status": "unauthorized", "message": message, "data": data, "status_code": status_code},
            status_code=status_code)

    @staticmethod
    def forbidden(data: Union[dict, None] = None, message: str = "Forbidden", status_code: int = 403):
        return JSONResponse(
            content={"status": "unauthorized", "message": message, "data": data, "status_code": status_code},
            status_code=status_code)

    @staticmethod
    def internal_server_error(data: Union[dict, None] = None, message: str = "Internal Server Error",
                              status_code: int = 500):
        return JSONResponse(
            content={"status": "internal_server_error", "message": message, "data": data, "status_code": status_code},
            status_code=status_code)

    @staticmethod
    def streaming_response(file_stream, media_type: str, file_name: str):
        return StreamingResponse(io.BytesIO(file_stream), media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        })
