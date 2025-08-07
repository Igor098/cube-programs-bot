from pydantic import BaseModel


class StatementFileReadSchema(BaseModel):
    filename: str
    url: str
    size: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "statement.pdf",
                "url": "https://yourdomain.ru/files/statement.pdf",
                "size": 15360
            }
        }
    }