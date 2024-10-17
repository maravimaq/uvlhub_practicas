import pytest
from unittest.mock import patch, MagicMock
from app.modules.notepad.services import NotepadService
from sqlalchemy.exc import IntegrityError


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


@pytest.fixture
def notepad_service():
    return NotepadService()


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"


# Test para obtener todos los Notepads por usuario
def test_get_all_by_user(notepad_service):
    with patch.object(notepad_service.repository, 'get_all_by_user') as mock_get_all:
        mock_notepads = [MagicMock(id=1), MagicMock(id=2)]
        mock_get_all.return_value = mock_notepads

        user_id = 1
        result = notepad_service.get_all_by_user(user_id)

        assert result == mock_notepads
        assert len(result) == 2
        mock_get_all.assert_called_once_with(user_id)


# Test para crear un Notepad
def test_create(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_notepad = MagicMock(id=1)
        mock_create.return_value = mock_notepad

        title = 'Test Notepad'
        body = 'Test Body'
        user_id = 1

        result = notepad_service.create(title=title, body=body, user_id=user_id)

        assert result == mock_notepad
        assert result.id == 1
        mock_create.assert_called_once_with(title=title, body=body, user_id=user_id)


# Test para actualizar un Notepad
def test_update(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_notepad = MagicMock(id=1)
        mock_update.return_value = mock_notepad

        notepad_id = 1
        title = 'Updated Notepad'
        body = 'Updated Body'

        result = notepad_service.update(notepad_id, title=title, body=body)

        assert result == mock_notepad
        mock_update.assert_called_once_with(notepad_id, title=title, body=body)

      
def test_create_invalid_data(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_create.side_effect = IntegrityError("Integrity constraint violated", None, None)

        title = ''  # Invalid title
        body = 'Test Body'
        user_id = 1

        with pytest.raises(IntegrityError):
            notepad_service.create(title=title, body=body, user_id=user_id)


# Test para eliminar un Notepad
def test_delete(notepad_service):
    with patch.object(notepad_service.repository, 'delete') as mock_delete:
        mock_delete.return_value = True

        notepad_id = 1
        result = notepad_service.delete(notepad_id)

        assert result is True
        mock_delete.assert_called_once_with(notepad_id)


# Test para obtener Notepads sin Notepads existentes
def test_get_all_by_user_no_notepads(notepad_service):
    with patch.object(notepad_service.repository, 'get_all_by_user') as mock_get_all:
        mock_get_all.return_value = []

        user_id = 1
        result = notepad_service.get_all_by_user(user_id)

        assert result == []
        mock_get_all.assert_called_once_with(user_id)


# Test para intentar actualizar un Notepad que no existe
def test_update_nonexistent_notepad(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_update.side_effect = Exception("Notepad not found")

        notepad_id = 99  # ID que no existe
        title = 'Updated Notepad'
        body = 'Updated Body'

        with pytest.raises(Exception, match="Notepad not found"):
            notepad_service.update(notepad_id, title=title, body=body)


# Test para intentar eliminar un Notepad que no existe
def test_delete_nonexistent_notepad(notepad_service):
    with patch.object(notepad_service.repository, 'delete') as mock_delete:
        mock_delete.side_effect = Exception("Notepad not found")

        notepad_id = 99  # ID que no existe

        with pytest.raises(Exception, match="Notepad not found"):
            notepad_service.delete(notepad_id)


# Test para crear un Notepad sin título
def test_create_notepad_without_title(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_create.side_effect = Exception("Title is required")

        title = ''  # Título vacío
        body = 'Test Body'
        user_id = 1

        with pytest.raises(Exception, match="Title is required"):
            notepad_service.create(title=title, body=body, user_id=user_id)


# Test para crear un Notepad sin cuerpo
def test_create_notepad_without_body(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_create.side_effect = Exception("Body is required")

        title = 'Test Notepad'
        body = ''  # Cuerpo vacío
        user_id = 1

        with pytest.raises(Exception, match="Body is required"):
            notepad_service.create(title=title, body=body, user_id=user_id)


def test_update_not_found(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_update.side_effect = Exception("Not Found")

        notepad_id = 99
        title = 'Updated Notepad'
        body = 'Updated Body'

        with pytest.raises(Exception):
            notepad_service.update(notepad_id, title=title, body=body)


# Delete notepad not found
def test_delete_not_found(notepad_service):
    with patch.object(notepad_service.repository, 'delete') as mock_delete:
        mock_delete.side_effect = Exception("Not Found")

        notepad_id = 99

        with pytest.raises(Exception):
            notepad_service.delete(notepad_id)


# Update notepad with invalid data
def test_update_invalid_data(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_update.side_effect = IntegrityError("Integrity constraint violated", None, None)

        notepad_id = 1
        title = ''  # Invalid title
        body = 'Updated Body'

        with pytest.raises(IntegrityError):
            notepad_service.update(notepad_id, title=title, body=body)


# Get notepad by ID successfully
def test_get_by_id(notepad_service):
    with patch.object(notepad_service.repository, 'get_by_id') as mock_get_by_id:
        mock_notepad = MagicMock(id=1)
        mock_get_by_id.return_value = mock_notepad

        result = notepad_service.get_by_id(1)

        assert result == mock_notepad
        mock_get_by_id.assert_called_once_with(1)


# Get notepad by ID not found
def test_get_by_id_not_found(notepad_service):
    with patch.object(notepad_service.repository, 'get_by_id') as mock_get_by_id:
        mock_get_by_id.side_effect = Exception("Not Found")

        with pytest.raises(Exception):
            notepad_service.get_by_id(99)


# Create multiple notepads
def test_create_multiple_notepads(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_notepad1 = MagicMock(id=1)
        mock_notepad2 = MagicMock(id=2)
        mock_create.side_effect = [mock_notepad1, mock_notepad2]

        result1 = notepad_service.create(title='Notepad 1', body='Body 1', user_id=1)
        result2 = notepad_service.create(title='Notepad 2', body='Body 2', user_id=1)

        assert result1.id == 1
        assert result2.id == 2
        mock_create.assert_any_call(title='Notepad 1', body='Body 1', user_id=1)
        mock_create.assert_any_call(title='Notepad 2', body='Body 2', user_id=1)


# Delete multiple notepads
def test_delete_multiple_notepads(notepad_service):
    with patch.object(notepad_service.repository, 'delete') as mock_delete:
        mock_delete.side_effect = [True, True]

        result1 = notepad_service.delete(1)
        result2 = notepad_service.delete(2)

        assert result1 is True
        assert result2 is True
        mock_delete.assert_any_call(1)
        mock_delete.assert_any_call(2)


# Update multiple notepads
def test_update_multiple_notepads(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_notepad1 = MagicMock(id=1)
        mock_notepad2 = MagicMock(id=2)
        mock_update.side_effect = [mock_notepad1, mock_notepad2]

        result1 = notepad_service.update(1, 'Updated Notepad 1', 'Updated Body 1')
        result2 = notepad_service.update(2, 'Updated Notepad 2', 'Updated Body 2')

        assert result1 == mock_notepad1
        assert result2 == mock_notepad2
        mock_update.assert_any_call(1, 'Updated Notepad 1', 'Updated Body 1')
        mock_update.assert_any_call(2, 'Updated Notepad 2', 'Updated Body 2')


# Test notepad title length
def test_notepad_title_length(notepad_service):
    title = 'a' * 256  # Exceeds typical length limit
    body = 'Test Body'
    user_id = 1

    with pytest.raises(IntegrityError):
        notepad_service.create(title=title, body=body, user_id=user_id)


# Test notepad body length
def test_notepad_body_length(notepad_service):
    title = 'Test Notepad'
    body = 'b' * 5001  # Exceeds typical length limit
    user_id = 1

    with pytest.raises(IntegrityError):
        notepad_service.create(title=title, body=body, user_id=user_id)


# Create notepad with None body
def test_create_notepad_with_none_body(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_create.side_effect = IntegrityError("Integrity constraint violated", None, None)

        with pytest.raises(IntegrityError):
            notepad_service.create(title='Notepad Title', body=None, user_id=1)


# Update notepad with None title
def test_update_notepad_with_none_title(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_update.side_effect = IntegrityError("Integrity constraint violated", None, None)

        with pytest.raises(IntegrityError):
            notepad_service.update(1, title=None, body='Updated Body')


# Ensure get_all_by_user returns empty list when no notepads exist
def test_get_all_by_user_empty(notepad_service):
    with patch.object(notepad_service.repository, 'get_all_by_user') as mock_get_all:
        mock_get_all.return_value = []

        result = notepad_service.get_all_by_user(1)

        assert result == []
        mock_get_all.assert_called_once_with(1)


# Test updating a notepad with the same data
def test_update_same_data(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        notepad_id = 1
        title = 'Existing Notepad'
        body = 'Existing Body'

        result = notepad_service.update(notepad_id, title=title, body=body)

        assert result is not None
        mock_update.assert_called_once_with(notepad_id, title=title, body=body)


# Test delete method with None ID
def test_delete_with_none_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.delete(None)


# Test update method with None ID
def test_update_with_none_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.update(None, title='Updated Title', body='Updated Body')


# Test create method with None user_id
def test_create_with_none_user_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.create(title='Notepad', body='Body', user_id=None)


# Test get_by_id with None ID
def test_get_by_id_with_none_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.get_by_id(None)


# Test get_all_by_user with None user_id
def test_get_all_by_user_with_none_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.get_all_by_user(None)


# Create notepad with excessive data
def test_create_notepad_with_excessive_data(notepad_service):
    title = 'Test' * 100  # Excessive title length
    body = 'Body' * 1000  # Excessive body length
    user_id = 1

    with pytest.raises(IntegrityError):
        notepad_service.create(title=title, body=body, user_id=user_id)


# Update notepad with excessive data
def test_update_notepad_with_excessive_data(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        title = 'Test' * 100  # Excessive title length
        body = 'Body' * 1000  # Excessive body length

        with pytest.raises(IntegrityError):
            notepad_service.update(1, title=title, body=body)


# Attempt to delete a notepad with invalid data type
def test_delete_invalid_data_type(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.delete("invalid_id")


# Attempt to update a notepad with invalid data type
def test_update_invalid_data_type(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.update("invalid_id", title='Title', body='Body')


# Attempt to create a notepad with invalid user ID
def test_create_notepad_with_invalid_user_id(notepad_service):
    with pytest.raises(TypeError):
        notepad_service.create(title='Notepad', body='Body', user_id='invalid_user_id')
