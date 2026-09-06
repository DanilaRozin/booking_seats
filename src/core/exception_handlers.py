from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

ERROR_MESSAGES = {
    'missing': 'обязательное поле не заполнено',
}


async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """Приводит ошибки валидации запроса (включая невалидный JSON) к единому формату."""
    errors = exception.errors()

    if len(errors) == 1 and errors[0]['type'] == 'json_invalid':
        detail = 'Невалидный JSON в теле запроса.'
    else:
        messages = []
        for err in errors:
            field = '.'.join(str(part) for part in err['loc'] if part not in ('body', 'query', 'path'))
            if err['type'] == 'value_error' and 'ctx' in err and 'error' in err['ctx']:
                message = str(err['ctx']['error'])
            else:
                message = ERROR_MESSAGES.get(err['type'], err['msg'])
            messages.append(f'{field}: {message}' if field else message)
        detail = '; '.join(messages)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'status_code': status.HTTP_422_UNPROCESSABLE_ENTITY,
            'message': detail,
        },
    )


async def http_exception_handler(
    request: Request,
    exception: HTTPException,
) -> JSONResponse:
    """Обрабатывает HTTP-исключение и изменяет названия полей ответа."""
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'status_code': exception.status_code,
            'message': exception.detail,
        },
        headers=exception.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики исключений приложения."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
