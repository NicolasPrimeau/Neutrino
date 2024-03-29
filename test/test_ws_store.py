

from chalicelib import ws_store


def test_register():
    ws_store.delete_item("session1")
    assert ws_store.insert_new_connection("session1", "connection1") == {"connection1"}


def test_get_connections():
    ws_store.delete_item("session1")
    ws_store.insert_new_connection("session1", "connection1")
    assert ws_store.get_connection_ids_for_session("session1") == {"connection1"}


def test_repeat():
    ws_store.delete_item("session1")
    ws_store.insert_new_connection("session1", "connection1")
    assert ws_store.insert_new_connection("session1", "connection1") == {"connection1"}


def test_new_connections():
    ws_store.delete_item("session1")
    ws_store.insert_new_connection("session1", "connection1")
    assert ws_store.insert_new_connection("session1", "connection2") == {"connection1", "connection2"}


def test_deregister():
    ws_store.delete_item("session1")
    ws_store.insert_new_connection("session1", "connection1")
    assert ws_store.insert_new_connection("session1", "connection2") == {"connection1", "connection2"}
    assert ws_store.remove_connection("session1", "connection1") == {"connection2"}


def test_save_text():
    ws_store.delete_item("session1")
    ws_store.save_source_code("session1", "test code", 0)
    assert ws_store.get_source_code("session1") == ("test code", 0)


def test_load_not_exist():
    ws_store.delete_item("session1")
    assert ws_store.get_source_code("session1") == (None, None)
