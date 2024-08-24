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
    document.getElementById('category').addEventListener('change', loadSubskills);
});

function loadSubskills() {
    const categoryId = document.getElementById('category').value;
    const skillSelect = document.getElementById('skills');

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
    const formElements = document.querySelectorAll('#email, #dob, #country, #city, #bio, #category, #skills');
    const editButton = document.getElementById('edit-profile-button');
    const saveButton = document.getElementById('save-changes-button');
    const cancelButton = document.getElementById('cancel-edit-button');
    const imageUploadGroup = document.querySelector('.image-upload-group');

    if (editButton.style.display !== 'none' && !cancel) {
        formElements.forEach(element => {
            element.removeAttribute('readonly');
            element.classList.add('editable');
            if (element.tagName === 'SELECT') {
                element.disabled = false;
            }
        });
        imageUploadGroup.style.display = 'flex';
        editButton.style.display = 'none';
        saveButton.style.display = 'block';
        cancelButton.style.display = 'block';
    } else {
        formElements.forEach(element => {
            element.setAttribute('readonly', true);
            element.classList.remove('editable');
            if (element.tagName === 'SELECT') {
                element.disabled = true;
            }
            if (cancel) {
                element.value = element.defaultValue;
            }
        });
        imageUploadGroup.style.display = 'none';
        editButton.style.display = 'block';
        saveButton.style.display = 'none';
        cancelButton.style.display = 'none';
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
