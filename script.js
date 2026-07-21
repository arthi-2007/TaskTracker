document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.task-checkbox');

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const taskId = this.dataset.id;

            fetch('/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: taskId }),
            })
            .then(response => {
                if (response.ok) {
                    // Optionally show visual feedback
                    this.parentElement.classList.toggle('done');
                } else {
                    alert('Failed to update task status.');
                }
            });
        });
    });
});

