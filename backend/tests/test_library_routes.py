import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.presentation.api.v1.library.routes import create_book, borrow_book, return_book
from app.presentation.api.v1.library.schemas import CreateBookRequest, BorrowBookRequest, ReturnBookRequest

class MockUser:
    def __init__(self, tenant_id, id_='u1'):
        self.tenant_id = tenant_id
        self.id = id_

class MockBookRepo:
    def __init__(self):
        self.books = {}
    async def create(self, data):
        class B: pass
        b = B(); b.id = 'B1'; b.title = data.get('title'); b.author = data.get('author'); b.available_copies = data.get('available_copies'); b.total_copies = data.get('total_copies')
        self.books['B1'] = b
        return b
    async def get_by_id(self, book_id):
        return self.books.get(book_id)
    async def update(self, book_id, data):
        b = self.books.get(book_id)
        if not b: return None
        for k,v in data.items(): setattr(b, k, v)
        return b

class MockBorrowingRepo:
    def __init__(self):
        self.created = {}
    async def create(self, data):
        class R: pass
        r = R(); r.id = 'BR1'; r.due_date = datetime.utcnow() + timedelta(days=14); r.book_id = data.get('book_id')
        self.created['BR1'] = r
        return r
    async def get_by_id(self, borrowing_id):
        return self.created.get(borrowing_id)
    async def update(self, borrowing_id, data):
        b = self.created.get(borrowing_id)
        if not b: return None
        for k,v in data.items(): setattr(b, k, v)
        return b


@pytest.mark.asyncio
async def test_create_and_borrow_and_return():
    user = MockUser('t1')
    book_repo = MockBookRepo()
    borrowing_repo = MockBorrowingRepo()

    # create book
    req = CreateBookRequest(title='Intro', author='Author X', category='CS', total_copies=2)
    book_resp = await create_book(req, current_user=user, book_repo=book_repo)
    assert book_resp.title == 'Intro'

    # borrow
    book_repo.books['B1'].available_copies = 2
    borrow_req = BorrowBookRequest(student_id='STU1', book_id='B1', days=7)
    res = await borrow_book(borrow_req, current_user=user, book_repo=book_repo, borrowing_repo=borrowing_repo)
    assert 'borrowing_id' in res

    # return
    ret_req = ReturnBookRequest(borrowing_id='BR1')
    ret = await return_book(ret_req, current_user=user, book_repo=book_repo, borrowing_repo=borrowing_repo)
    assert ret['status'] == 'returned'
