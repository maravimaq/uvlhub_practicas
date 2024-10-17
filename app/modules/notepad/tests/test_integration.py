import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from flask_login import current_user


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_get_notepad(test_client):
    """
    Test retrieving a specific notepad via GET request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a notepad
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad2',
        'body': 'This is the body of notepad2.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Get the notepad ID from the database
    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad = Notepad.query.filter_by(title='Notepad2', user_id=current_user.id).first()
        assert notepad is not None, "Notepad was not found in the database."

    # Access the notepad detail page
    response = test_client.get(f'/notepad/{notepad.id}')
    assert response.status_code == 200, "The notepad detail page could not be accessed."
    assert b'Notepad2' in response.data, "The notepad title is not present on the page."

    logout(test_client)


def test_edit_notepad(test_client):
    """
    Test editing a notepad via POST request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a notepad
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad3',
        'body': 'This is the body of notepad3.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Get the notepad ID from the database
    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad = Notepad.query.filter_by(title='Notepad3', user_id=current_user.id).first()
        assert notepad is not None, "Notepad was not found in the database."

    # Edit the notepad
    response = test_client.post(f'/notepad/edit/{notepad.id}', data={
        'title': 'Notepad3 Edited',
        'body': 'This is the edited body of notepad3.'
    }, follow_redirects=True)
    assert response.status_code == 200, "The notepad could not be edited."

    # Check that the notepad was updated
    with test_client.application.app_context():
        notepad = Notepad.query.get(notepad.id)
        assert notepad.title == 'Notepad3 Edited', "The notepad title was not updated."
        assert notepad.body == 'This is the edited body of notepad3.', "The notepad body was not updated."

    logout(test_client)


def test_delete_notepad(test_client):
    """
    Test deleting a notepad via POST request.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Create a notepad
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad4',
        'body': 'This is the body of notepad4.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Get the notepad ID from the database
    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad = Notepad.query.filter_by(title='Notepad4', user_id=current_user.id).first()
        assert notepad is not None, "Notepad was not found in the database."

    # Delete the notepad
    response = test_client.post(f'/notepad/delete/{notepad.id}', follow_redirects=True)
    assert response.status_code == 200, "The notepad could not be deleted."

    # Check that the notepad was deleted
    with test_client.application.app_context():
        notepad = Notepad.query.get(notepad.id)
        assert notepad is None, "The notepad was not deleted."

    logout(test_client)


def test_access_notepad_unauthenticated(test_client):
    """
    Test that unauthenticated users cannot access the notepad detail page.
    """
    # Crear una nota como usuario autenticado
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post('/notepad/create', data={
        'title': 'Notepad5',
        'body': 'This is the body of notepad5.'
    }, follow_redirects=True)
    assert response.status_code == 200

    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad = Notepad.query.filter_by(title='Notepad5').first()
    
    # Desloguearse
    logout(test_client)

    # Intentar acceder a la nota sin estar autenticado
    response = test_client.get(f'/notepad/{notepad.id}')
    assert response.status_code == 302, "Unauthenticated users should be redirected to the login page."
    assert b'Redirecting' in response.data


def test_create_notepad_without_title(test_client):
    """
    Test that a notepad cannot be created without a title.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    response = test_client.post('/notepad/create', data={
        'title': '',
        'body': 'This note has no title.'
    }, follow_redirects=True)

    assert b'Title is required' in response.data, "The notepad should not be created without a title."

    logout(test_client)


def test_update_notepad_with_existing_title(test_client):
    """
    Test updating a notepad with a title that already exists.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    # Crear dos notas
    test_client.post('/notepad/create', data={
        'title': 'Notepad6',
        'body': 'Body of notepad 6.'
    }, follow_redirects=True)
    test_client.post('/notepad/create', data={
        'title': 'Notepad7',
        'body': 'Body of notepad 7.'
    }, follow_redirects=True)

    # Obtener IDs
    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad6 = Notepad.query.filter_by(title='Notepad6').first()
        notepad7 = Notepad.query.filter_by(title='Notepad7').first()

    # Intentar cambiar el título de notepad7 al título de notepad6
    response = test_client.post(f'/notepad/edit/{notepad7.id}', data={
        'title': 'Notepad6',
        'body': 'Updated body of notepad7.'
    }, follow_redirects=True)

    assert b'Title already exists' in response.data, "The notepad should not be updated with a duplicate title."

    logout(test_client)


def test_notepad_title_length_limit(test_client):
    """
    Test that a notepad cannot be created with a title exceeding the length limit.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    title = 'a' * 256  # Exceeds typical title length limit
    response = test_client.post('/notepad/create', data={
        'title': title,
        'body': 'This note has an excessively long title.'
    }, follow_redirects=True)

    assert b'Title must not exceed 255 characters' in response.data, "The notepad should not be created with an excessively long title."

    logout(test_client)


def test_notepad_body_length_limit(test_client):
    """
    Test that a notepad cannot be created with a body exceeding the length limit.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    body = 'a' * 5001  # Exceeds typical body length limit
    response = test_client.post('/notepad/create', data={
        'title': 'Long Body Notepad',
        'body': body
    }, follow_redirects=True)

    assert b'Body must not exceed 5000 characters' in response.data, "The notepad should not be created with an excessively long body."

    logout(test_client)

 
def test_create_duplicate_notepad(test_client):
    """
    Test that a notepad with a duplicate title cannot be created.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    # Crear una primera nota
    response = test_client.post('/notepad/create', data={
        'title': 'Duplicate Notepad',
        'body': 'First note body.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Intentar crear una segunda nota con el mismo título
    response = test_client.post('/notepad/create', data={
        'title': 'Duplicate Notepad',
        'body': 'Second note body.'
    }, follow_redirects=True)

    assert b'Title already exists' in response.data, "The second notepad with a duplicate title should not be created."

    logout(test_client)


def test_access_nonexistent_notepad(test_client):
    """
    Test that accessing a nonexistent notepad returns a 404 error.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    # Intentar acceder a una nota con un ID que no existe
    response = test_client.get('/notepad/99999', follow_redirects=True)
    assert response.status_code == 404, "Accessing a nonexistent notepad should return a 404 error."

    logout(test_client)
    

def test_edit_notepad_without_changes(test_client):
    """
    Test editing a notepad without making any changes.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    # Crear una nota
    response = test_client.post('/notepad/create', data={
        'title': 'Unchanged Notepad',
        'body': 'This is an unchanged notepad.'
    }, follow_redirects=True)
    assert response.status_code == 200

    with test_client.application.app_context():
        from app.modules.notepad.models import Notepad
        notepad = Notepad.query.filter_by(title='Unchanged Notepad').first()

    # Intentar editar la nota sin hacer cambios
    response = test_client.post(f'/notepad/edit/{notepad.id}', data={
        'title': 'Unchanged Notepad',
        'body': 'This is an unchanged notepad.'
    }, follow_redirects=True)

    assert b'No changes were made' in response.data, "Editing a notepad without changes should not update the database."

    logout(test_client)
    

def test_delete_notepad_from_another_user(test_client):
    """
    Test that a user cannot delete a notepad that belongs to another user.
    """
    # Crear un nuevo usuario y nota
    with test_client.application.app_context():
        new_user = User(email='anotheruser@example.com', password='password1234')
        db.session.add(new_user)
        db.session.commit()

        from app.modules.notepad.models import Notepad
        notepad = Notepad(title='Another User Notepad', body='Another user\'s notepad.', user_id=new_user.id)
        db.session.add(notepad)
        db.session.commit()

    # Intentar eliminar la nota de otro usuario como usuario autenticado
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    response = test_client.post(f'/notepad/delete/{notepad.id}', follow_redirects=True)
    assert b'Permission denied' in response.data, "Users should not be able to delete notepads from other users."

    logout(test_client)
    

def test_edit_notepad_from_another_user(test_client):
    """
    Test that a user cannot edit a notepad that belongs to another user.
    """
    # Crear un nuevo usuario y nota
    with test_client.application.app_context():
        new_user = User(email='anotheruser@example.com', password='password1234')
        db.session.add(new_user)
        db.session.commit()

        from app.modules.notepad.models import Notepad
        notepad = Notepad(title='Another User Notepad', body='Another user\'s notepad.', user_id=new_user.id)
        db.session.add(notepad)
        db.session.commit()

    # Intentar editar la nota de otro usuario como usuario autenticado
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200

    response = test_client.post(f'/notepad/edit/{notepad.id}', data={
        'title': 'Unauthorized Edit',
        'body': 'Trying to edit another user\'s notepad.'
    }, follow_redirects=True)
    assert b'Permission denied' in response.data, "Users should not be able to edit notepads from other users."

    logout(test_client)


def test_access_notepad_list_unauthenticated(test_client):
    """
    Test that unauthenticated users cannot access the notepad list.
    """
    response = test_client.get('/notepad/list', follow_redirects=True)
    assert response.status_code == 302, "Unauthenticated users should be redirected to the login page."
    assert b'Redirecting' in response.data, "Unauthenticated users should not be able to access the notepad list."
