from typing import Optional

from pydantic import Field, BaseModel, HttpUrl, model_validator


class ProgramCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, title="Название программы",
                      description="В данное поле вводится название программы",
                      examples=["Программирование роботов", "Системное администрирование"])

    description: Optional[str] = Field(None, max_length=512, title="Описание программы",
                                       description="В данное поле вводится описание программы")

    min_age: int = Field(..., ge=5, le=13, title="Минимальный возраст",
                         description="В данное поле вводится минимальный возраст", examples=[6, 12])

    max_age: int = Field(..., ge=8, le=18, title="Максимальный возраст",
                         description="В данное поле вводится максимальный возраст", examples=[11, 18])

    navigator_link: HttpUrl = Field(..., max_length=512, title="Ссылка на навигатор",
                                    description="В данное поле вводится ссылка на навигатор",
                                    examples=["https://www.google.com", "https://www.yandex.ru/"])

    requirements: Optional[str] = Field(None, max_length=1000, title="Требования",
                                        description="В данное поле вводится дополнительные требования к программе")

    image_url: Optional[HttpUrl] = Field(None, max_length=512, title="Ссылка на изображение",
                                         description="В данное поле вводится ссылка на изображение",
                                         examples=["https://www.google.com", "https://www.yandex.ru/"])

    @model_validator(mode='before')
    def check_age_range(cls, values):
        min_age = values.get('min_age')
        max_age = values.get('max_age')
        if min_age and max_age and min_age > max_age:
            raise ValueError('min_age не может быть больше max_age')
        return values

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Робототехника Lego Spike Prime",
                    "description": "В процессе обучения по программе Lego SPIKE Prime обучающиеся научатся "
                                   "конструированию и навыкам начального программированию роботов. Конструирование "
                                   "моделей становится не просто увлекательным, но и познавательным занятием – дети на "
                                   "практике постигают межпредметные взаимосвязи физических процессов и явлений, "
                                   "решают технологические и исследовательские задачи.",
                    "min_age": 9,
                    "max_age": 11,
                    "navigator_link": "https://www.google.com",
                    "requirements": None,
                    "image_url": "https://www.google.com",
                }
            ]
        }
    }


class ProgramUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=50, title="Название программы",
                                description="В данное поле вводится название программы",
                                examples=["Программирование роботов", "Системное администрирование"])

    description: Optional[str] = Field(default=None, max_length=512, title="Описание программы",
                                       description="В данное поле вводится описание программы")

    min_age: Optional[int] = Field(default=None, ge=5, le=13, title="Минимальный возраст",
                                   description="В данное поле вводится минимальный возраст", examples=[6, 12])

    max_age: Optional[int] = Field(default=None, ge=8, le=18, title="Максимальный возраст",
                                   description="В данное поле вводится максимальный возраст", examples=[11, 18])

    navigator_link: Optional[HttpUrl] = Field(default=None, max_length=512, title="Ссылка на навигатор",
                                              description="В данное поле вводится ссылка на навигатор",
                                              examples=["https://www.google.com", "https://www.yandex.ru/"])

    requirements: Optional[str] = Field(default=None, max_length=1000, title="Требования",
                                        description="В данное поле вводится дополнительные требования к программе")

    image_url: Optional[HttpUrl] = Field(default=None, max_length=512, title="Ссылка на изображение",
                                         description="В данное поле вводится ссылка на изображение",
                                         examples=["https://www.google.com", "https://www.yandex.ru/"])

    is_active: Optional[bool] = Field(default=None, title="Активность программы",
                                      description="В данное поле вводится активность программы",
                                      examples=[True, False])

    @model_validator(mode='before')
    def check_age_range(cls, values):
        min_age = values.get('min_age')
        max_age = values.get('max_age')
        if min_age and max_age and min_age > max_age:
            raise ValueError('min_age не может быть больше max_age')
        return values

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Робототехника Lego Spike Prime",
                    "min_age": 8,
                    "max_age": 11,
                },
                {
                    "navigator_link": "https://www.google.com",
                },
                {
                    "is_active": True,
                },
                {
                    "description": "В процессе обучения по программе Lego SPIKE Prime обучающиеся научатся "
                                   "конструированию и навыкам начального программированию роботов. Конструирование "
                                   "моделей становится не просто увлекательным, но и познавательным занятием – дети на "
                                   "практике постигают межпредметные взаимосвязи физических процессов и явлений, "
                                   "решают технологические и исследовательские задачи.",
                },
            ]
        }
    }


class ProgramSchema(BaseModel):
    id: int = Field(..., title="ID программы", description="Данное поле содержит ID программы", examples=[1, 25])

    name: str = Field(..., min_length=3, max_length=50, title="Название программы",
                      description="Данное поле содержит название программы",
                      examples=["Программирование роботов", "Системное администрирование"])

    description: Optional[str] = Field(None, max_length=512, title="Описание программы",
                                       description="Данное поле содержит описание программы",
                                       examples=["В процессе обучения по программе Lego SPIKE Prime обучающиеся "
                                                 "научатся конструированию и навыкам начального программированию "
                                                 "роботов."
                                                 "Конструирование моделей становится не просто увлекательным, "
                                                 "но и познавательным занятием – дети на практике постигают "
                                                 "межпредметные взаимосвязи физических процессов и явлений, "]
                                       )

    min_age: int = Field(..., ge=5, le=13, title="Минимальный возраст",
                         description="Данное поле содержит минимальный возраст",
                         examples=[6, 12])

    max_age: int = Field(..., ge=8, le=18, title="Максимальный возраст",
                         description="Данное поле содержит максимальный возраст",
                         examples=[11, 18])

    navigator_link: HttpUrl = Field(..., max_length=512, title="Ссылка на навигатор",
                                    description="Данное поле содержит ссылку на навигатор",
                                    examples=["https://www.google.com", "https://www.yandex.ru/"])

    requirements: Optional[str] = Field(None, max_length=1000, title="Требования",
                                        description="Данное поле содержит дополнительные требования к программе")

    image_url: Optional[HttpUrl] = Field(None, max_length=512, title="Ссылка на изображение",
                                         description="Данное поле содержит ссылку на изображение",
                                         examples=["https://www.google.com", "https://www.yandex.ru/"])

    is_active: bool = Field(..., title="Активность программы",
                            description="Данное поле содержит активность программы",
                            examples=[True, False])

    model_config = {
        "from_attributes": True
    }


class ProgramFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
