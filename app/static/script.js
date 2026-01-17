document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('todo-form');
    const list = document.getElementById('todo-list');
    const editId = document.getElementById('edit-id');
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    const statusSelect = document.getElementById('status');
    const photoInput = document.getElementById('photo');
    const alertDiv = document.getElementById('alert');

    function showAlert(message) {
        alertDiv.textContent = message;
        alertDiv.style.display = 'block';
        setTimeout(() => alertDiv.style.display = 'none', 3000);
    }

    function loadTodos() {
        fetch('/api/todos')
            .then(res => res.json())
            .then(todos => {
                list.innerHTML = '';
                todos.forEach(todo => {
                    const li = document.createElement('li');
                    li.className = todo.status === 'done' ? 'done' : '';
                    li.innerHTML = `
                        <div>
                            <strong>${todo.title}</strong><br>
                            ${todo.description || ''}<br>
                            Status: ${todo.status}<br>
                            Created: ${todo.created_at}
                        </div>
                        ${todo.photo ? `<img src="/uploads/${todo.photo}" alt="Photo">` : ''}
                        <div class="actions">
                            <button class="edit" onclick="editTodo(${todo.id}, '${todo.title}', '${todo.description || ''}', '${todo.status}')">Edit</button>
                            <button onclick="deleteTodo(${todo.id})">Hapus</button>
                        </div>
                    `;
                    list.appendChild(li);
                });
            })
            .catch(err => showAlert('Error loading todos: ' + err));
    }

    form.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('title', titleInput.value);
        formData.append('description', descInput.value);
        formData.append('status', statusSelect.value);
        if (photoInput.files[0]) formData.append('photo', photoInput.files[0]);

        const method = editId.value ? 'PUT' : 'POST';
        const url = editId.value ? `/api/todos/${editId.value}` : '/api/todos';

        fetch(url, { method, body: formData })
            .then(res => {
                if (!res.ok) throw new Error('Network error');
                loadTodos();
                form.reset();
                editId.value = '';
                form.querySelector('button').textContent = 'Tambah Todo';
            })
            .catch(err => showAlert('Error saving todo: ' + err));
    });

    window.editTodo = (id, title, desc, status) => {
        editId.value = id;
        titleInput.value = title;
        descInput.value = desc;
        statusSelect.value = status;
        form.querySelector('button').textContent = 'Update Todo';
    };

    window.deleteTodo = id => {
        if (confirm('Yakin hapus?')) {
            fetch(`/api/todos/${id}`, { method: 'DELETE' })
                .then(() => loadTodos())
                .catch(err => showAlert('Error deleting todo: ' + err));
        }
    };

    loadTodos();
});