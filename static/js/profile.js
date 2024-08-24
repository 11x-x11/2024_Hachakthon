document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    form.addEventListener('submit', function(event) {
        const email = document.getElementById('email').value;
        const dob = document.getElementById('dob').value;

        if (!email || !dob) {
            alert('Please fill in all required fields.');
            event.preventDefault();
        }
    });

    // Attach the loadSubskills function to the category change event
    document.getElementById('category').addEventListener('change', () => loadSubskills('skills'));
    document.getElementById('interested_category').addEventListener('change', () => loadSubskills('interested_skills'));

});

function loadSubskills(skillType = 'skills') {
    const categorySelectId = skillType === 'skills' ? 'category' : 'interested_category';
    const skillSelectId = skillType === 'skills' ? 'skills' : 'interested_skills';

    const categoryId = document.getElementById(categorySelectId).value;
    const skillSelect = document.getElementById(skillSelectId);

    // Clear previous skill options
    skillSelect.innerHTML = '';

    if (categoryId) {
        fetch(`/get_skills_by_category?category_id=${categoryId}`)
            .then(response => response.json())
            .then(data => {
                if (data.skills.length > 0) {
                    data.skills.forEach(skill => {
                        const option = document.createElement('option');
                        option.value = skill.id;
                        option.textContent = skill.name;
                        skillSelect.appendChild(option);
                    });
                } else {
                    skillSelect.innerHTML = '<option value="">No skills available</option>';
                }
            })
            .catch(error => {
                console.error('Error fetching skills:', error);
                skillSelect.innerHTML = '<option value="">Error loading skills</option>';
            });
    }
}

function toggleEditMode(cancel = false) {
    const isEditMode = !cancel;

    const readOnlyFields = document.querySelectorAll('#email, #dob, #bio');
    const disabledFields = document.querySelectorAll('#country, #city, #category, #skills, #interested_category, #interested_skills');

    const editButton = document.getElementById('edit-profile-button');
    const saveButton = document.getElementById('save-changes-button');
    const cancelButton = document.getElementById('cancel-edit-button');
    const imageUploadGroup = document.querySelector('.image-upload-group');

    // Toggle readonly for input and textarea fields
    readOnlyFields.forEach(field => {
        if (isEditMode) {
            field.removeAttribute('readonly');
        } else {
            field.setAttribute('readonly', 'readonly');
        }
    });

    // Toggle disabled for select fields
    disabledFields.forEach(field => {
        if (isEditMode) {
            field.removeAttribute('disabled');
        } else {
            field.setAttribute('disabled', 'disabled');
        }
    });

    // Toggle buttons and image upload section
    if (isEditMode) {
        editButton.style.display = 'none';
        saveButton.style.display = 'inline-block';
        cancelButton.style.display = 'inline-block';
        imageUploadGroup.style.display = 'block'; // Show the image upload section
    } else {
        editButton.style.display = 'inline-block';
        saveButton.style.display = 'none';
        cancelButton.style.display = 'none';
        imageUploadGroup.style.display = 'none'; // Hide the image upload section
    }
}

// Optional: Auto-hide flash messages after a certain time
setTimeout(() => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => msg.style.display = 'none');
}, 5000);

function loadCities() {
    const countryCode = document.getElementById('country').value;
    const citySelect = document.getElementById('city');

    citySelect.innerHTML = '<option value="">Select a city</option>';

    if (countryCode) {
        fetch(`/get_cities?country=${countryCode}`)
            .then(response => response.json())
            .then(data => {
                data.cities.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    citySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching cities:', error));
    }
}
