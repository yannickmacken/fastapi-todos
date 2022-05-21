from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID

from starlette.responses import JSONResponse


class NegativeNumberException(Exception):

    def __init__(self, books_to_return):
        self.books_to_return = books_to_return



app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(title='description of book', min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=11)

    class Config:
        schema_extra = {
                "example": {"id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Book 1",
                "author": "John Appleseed",
                "description": "A biography of John Appleseed.",
                "rating": 8
                }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(title='description of book', min_length=1, max_length=100)


BOOKS = []

@app.post('/books/login')
async def book_login(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}


@app.post('/books/login_to_get_book')  # Get username and password from Form, and get book ID from query
async def book_login(book_id: UUID, username: str = Form(...), password: str = Form(...)):
    if username == 'a' and password == 'b':
        for book in BOOKS:
            if book.id == book_id:
                return book
        raise raise_item_cannot_be_found_exception()
    raise HTTPException(status_code=403, detail="Wrong password or user name.")


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):  # This gets the header from the request
    return {"Random-Header": random_header}


@app.get('/')
async def read_all_books(books_to_return: Optional[int] = None):
    if len(BOOKS)<1:
        create_books_no_api()
    if books_to_return:
        if books_to_return < 0:
            raise NegativeNumberException(books_to_return=books_to_return)
        return BOOKS[:books_to_return]
    return BOOKS


@app.get('/{book_id}')
async def read_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_cannot_be_found_exception()


@app.get('/rating/{book_id}', response_model=BookNoRating)  # Response model replaces return with other model
async def read_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_cannot_be_found_exception()


@app.post('/', status_code=status.HTTP_201_CREATED)
async def post_book(book: Book):
    BOOKS.append(book)
    return book


@app.put('/{book_id}')
async def update_book(book_id: UUID, book: Book):
    for i, existing_book in enumerate(BOOKS):
        if existing_book.id == book_id:
            BOOKS[i] = book
            return BOOKS[i]
    raise raise_item_cannot_be_found_exception()


@app.delete('/{book_id}')
async def delete_book(book_id: UUID):
    for i, book in enumerate(BOOKS):
        if book.id == book_id:
            BOOKS.pop(i)
            return f"Book with id {book_id} deleted."
    raise raise_item_cannot_be_found_exception()


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):
    return JSONResponse(status_code=418, content={"message": "Hey, why do you want a negative number of books?"
                                                             "You need to read more!"})



def create_books_no_api():
    book1 = Book(id='5448a92d-eec3-4b21-b344-5ff9696db5e7',
                 title='title1',
                 author='author1',
                 description='descr1',
                 rating=6)
    book2 = Book(id='5448a92d-eec4-4b21-b344-5ff9696db5e7',
                 title='title2',
                 author='author2',
                 description='descr2',
                 rating=7)
    book3 = Book(id='5448a92d-eec3-4b31-b344-5ff9696db5e7',
                 title='title3',
                 author='author3',
                 description='descr3',
                 rating=5)
    book4 = Book(id='5448a92d-eec3-4b25-b344-5ff9696db5e7',
                 title='title4',
                 author='author4',
                 description='descr4',
                 rating=9)
    BOOKS.extend([book1, book2, book3, book4])


def raise_item_cannot_be_found_exception():
    return HTTPException(status_code=404, detail='Book not found',
                        headers={"X-Header-Error": "Nothing to be seen at the UUID"})
