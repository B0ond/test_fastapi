from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field, EmailStr, ConfigDict

app = FastAPI()

data = {
    "email": "abc@mail.ru",
    "bio": "Тролльлоло",
    "age": 12,

}

class UserSchema(BaseModel):
    email: EmailStr
    bio: str | None = Field(max_length=100)

    model_config = ConfigDict(extra="forbid")

users = []

@app.post("/users")
def add_user(user: UserSchema):
    users.append(user)
    return {"ok": True, "msg": "User is added"}

@app.get("/users")
def get_user() -> list[UserSchema]:
    return users
 
data_without_age = {
    "email": "abc@mail.ru",
    "bio": "Текст вместе с возврастом",
}


# class UserAgeSchema(UserSchema):
#     age: int = Field(ge=0, le=150)

user = UserSchema(**data_without_age)
# user_age = UserAgeSchema(**data)
# print(repr(user_age))
print(repr(user))



# books = [
#     {
#         "id":1,
#         "title": "Асинхронность в питоне",
#         "author": "Метью",
#     },
#     {
#         "id":2,
#         "title":"Backend developming in python",
#         "author": "<NAME>",
#     }
# ]
#
# @app.get(
#     "/books",
#     tags=["Книги"],
#     summary="Получить все книги"
# )
# def read_books():
#     return books
#
# @app.get(
#     "/books/{book_id}",
#     tags=["Книги"],
#     summary="Получить конкретную книгу"
# )
# def get_book(book_id: int):
#     for book in books:
#         if book["id"] == book_id:
#             return book
#     raise HTTPException(status_code=404, detail="Книга не найдена")
#
# class NewBook(BaseModel):
#     title: str
#     author: str
#
# @app.post("/books", tags=["Книги"])
# def create_book(new_book: NewBook):
#     books.append({
#         "id": len(books) + 1,
#         "tetle": new_book.title,
#         "author": new_book.author
#     })
#     return {"success": True, "message": "Книга успешно добавлена"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)