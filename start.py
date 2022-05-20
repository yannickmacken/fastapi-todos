from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI()


BOOKS = {
    '0': {'title': 'Title one', 'author': 'Author one'},
    '1': {'title': 'Title two', 'author': 'Author two'},
    '2': {'title': 'Title three', 'author': 'Author three'},
    '3': {'title': 'Title four', 'author': 'Author four'}
}


class DirectionName(Enum):
    north = 'North'
    east = 'East'
    south = 'South'
    west = 'West'


@app.get('/')
async def read_all_books(skip_book: Optional[str] = None):
    if BOOKS.get(skip_book):
        new_books = BOOKS.copy()
        new_books.pop(skip_book)
        return new_books
    return BOOKS


@app.get('/books/mybook')
async def read_fav_book():
    return {"book title": "fav book"}


@app.get('/directions/{direction_name}')
async def get_direction(direction_name: DirectionName):
    return {'Direction': direction_name}


@app.get('/books/{book_name}')  # Order matters here, if there is another books/... it is accessed first
async def read_book(book_name: str):
    return BOOKS[book_name]


@app.post('/')
async def create_book(book_title: str, book_author: str):
    for i in range(len(BOOKS)+1):
        if not BOOKS.get(str(i)):
            BOOKS.update({str(i): {'title': book_title, 'author': book_author}})
            return BOOKS[str(i)]


@app.put('/{book_name}')
async def update_book(book_name: str, book_title: Optional[str] = None, book_author: Optional[str] = None):
    book_information = {}
    if book_title:
        book_information.update({'title': book_title})
    if book_author:
        book_information.update({'author': book_author} )
    BOOKS[book_name].update(book_information)
    return book_information


@app.delete('/{book_name}')
async def delete_book(book_name: str):
    BOOKS.pop(book_name)
    return f"book {book_name} deleted."
