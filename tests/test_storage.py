import os
from storage.json_storage import JSONStorage

def test_storage_read_empty(test_storage, test_data_dir):
    filepath = os.path.join(test_data_dir, "nonexistent.json")
    result = test_storage.read(filepath, default=[])
    assert result == []

def test_storage_write_and_read(test_storage, test_data_dir):
    filepath = os.path.join(test_data_dir, "sample.json")
    data = [{"id": "item_1", "name": "Organic Apples", "qty": 10}]
    assert test_storage.write(filepath, data) is True
    
    read_data = test_storage.read(filepath)
    assert len(read_data) == 1
    assert read_data[0]["name"] == "Organic Apples"

def test_storage_crud_operations(test_storage, test_data_dir):
    filepath = os.path.join(test_data_dir, "crud_test.json")
    
    # 1. Insert
    item = {"id": "test_101", "title": "Artisan Bread", "quantity": 25}
    test_storage.insert(filepath, item)
    
    # 2. Find by id
    found = test_storage.find_by_id(filepath, "test_101")
    assert found is not None
    assert found["title"] == "Artisan Bread"
    
    # 3. Update
    updated = test_storage.update(filepath, "test_101", {"quantity": 18})
    assert updated["quantity"] == 18
    assert "updated_at" in updated
    
    # 4. Delete
    deleted = test_storage.delete(filepath, "test_101")
    assert deleted is True
    assert test_storage.find_by_id(filepath, "test_101") is None
