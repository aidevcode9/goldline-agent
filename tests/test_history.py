"""Tests for src/history.py — thread store CRUD."""

from src.history import new_thread_id, get_messages, save_messages, _thread_store


class TestNewThreadId:
    def test_returns_string(self):
        tid = new_thread_id()
        assert isinstance(tid, str)

    def test_unique_ids(self):
        ids = {new_thread_id() for _ in range(100)}
        assert len(ids) == 100


class TestMessageStore:
    def setup_method(self):
        _thread_store.clear()

    def test_empty_thread_returns_empty_list(self):
        assert get_messages("nonexistent") == []

    def test_save_and_retrieve(self):
        messages = [{"role": "user", "content": "hello"}]
        save_messages("t1", messages)
        assert get_messages("t1") == messages

    def test_overwrite(self):
        save_messages("t1", [{"role": "user", "content": "first"}])
        save_messages("t1", [{"role": "user", "content": "second"}])
        assert get_messages("t1") == [{"role": "user", "content": "second"}]

    def test_separate_threads(self):
        save_messages("t1", [{"role": "user", "content": "thread1"}])
        save_messages("t2", [{"role": "user", "content": "thread2"}])
        assert get_messages("t1")[0]["content"] == "thread1"
        assert get_messages("t2")[0]["content"] == "thread2"
