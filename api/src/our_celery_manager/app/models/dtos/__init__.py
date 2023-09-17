from pydantic import BaseModel


class OCMBaseModel(BaseModel):

    @classmethod
    def from_list(cls, tpl):
        instance = cls(**{k: v for k, v in zip(cls.__fields__.keys(), tpl)})
        return instance