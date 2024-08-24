document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    form.addEventListener('submit', function(event) {
        const email = document.getElementById('email').value;
        const dob = document.getElementById('dob').value;

        // Example of additional client-side validation
        if (!email || !dob) {
            alert('Please fill in all required fields.');
            event.preventDefault();
        }
    });
});

function toggleEditMode(cancel = false) {
    const formElements = document.querySelectorAll('#email, #dob, #latitude, #longitude, #bio');
    const editButton = document.getElementById('edit-profile-button');
    const saveButton = document.getElementById('save-changes-button');
    const cancelButton = document.getElementById('cancel-edit-button');
    const imageUploadGroup = document.querySelector('.image-upload-group');
    
    if (editButton.style.display !== 'none' && !cancel) {
        // Switch to edit mode
        formElements.forEach(element => {
            element.removeAttribute('readonly');
            element.classList.add('editable');
        });
        imageUploadGroup.style.display = 'flex';
        editButton.style.display = 'none';
        saveButton.style.display = 'block';
        cancelButton.style.display = 'block';
    } else {
        // Switch to view mode
        formElements.forEach(element => {
            element.setAttribute('readonly', true);
            element.classList.remove('editable');
            // Optionally reset values if canceling edit
            if (cancel) {
                element.value = element.defaultValue;
            }
        });
        imageUploadGroup.style.display = 'none';
        editButton.style.display = 'block';
        saveButton.style.display = 'none';
        cancelButton.style.display = 'none';
        // Reset file input if canceling
        if (cancel) {
            document.getElementById('profile_image').value = '';
        }
    }
}

// Optional: Auto-hide flash messages after a certain time
setTimeout(() => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => msg.style.display = 'none');
}, 5000);