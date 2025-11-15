document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });

    // --- ПОЧАТОК ЗМІН: Нова логіка підтвердження зміни ролі ---
    const roleUpdateForms = document.querySelectorAll('.role-update-form');
    roleUpdateForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {

            // Знаходимо вибрану роль у цій конкретній формі
            const select = form.querySelector('select[name="role"]');
            const selectedRole = select.options[select.selectedIndex].text;

            // Формуємо динамічне повідомлення
            const message = `Are you sure you want to change this user's role to "${selectedRole.trim()}"?`;

            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    // --- КІНЕЦЬ ЗМІН ---
});