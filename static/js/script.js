document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const songInputsContainer = document.querySelector('.song-inputs');
    const addSongBtn = document.getElementById('add-song');
    const getRecommendationsBtn = document.getElementById('get-recommendations');
    const sliderOptions = document.querySelectorAll('.slider-option');
    const sliderHighlight = document.querySelector('.slider-highlight');
    const recommendationDescription = document.querySelector('.recommendation-description');
    const loader = document.querySelector('.loader');
    const recommendationsContainer = document.querySelector('.recommendations');
    const quickRecommendationsList = document.querySelector('.quick-recommendations .recommendation-list');
    const advancedRecommendationsList = document.querySelector('.advanced-recommendations .recommendation-list');
    const errorMessage = document.querySelector('.error-message');
    const errorMessageText = document.querySelector('.error-message p');
    
    // Set default recommendation type
    let recommendationType = 'quick';
    
    // Description texts for each recommendation type
    const descriptions = {
        'quick': 'Quick: Faster results based on song similarities',
        'advanced': 'Advanced: More accurate recommendations using clustering algorithms',
        'both': 'Both: Compare results from both recommendation methods'
    };
    
    // Add event listeners
    addSongBtn.addEventListener('click', addSongInput);
    getRecommendationsBtn.addEventListener('click', getRecommendations);
    
    // Add initial song input removal listener
    addRemoveSongListener(document.querySelector('.remove-song'));
    
    // Setup slider options
    sliderOptions.forEach((option, index) => {
        option.addEventListener('click', () => {
            updateSlider(option, index);
        });
        
        // Add active class to first option
        if (index === 0) {
            option.classList.add('active');
        }
    });
    
    /**
     * Adds a new song input row
     */
    function addSongInput() {
        const songInputRow = document.createElement('div');
        songInputRow.className = 'song-input-row';
        songInputRow.innerHTML = `
            <input type="text" placeholder="Song Name" class="song-name">
            <input type="number" placeholder="Year" class="song-year" min="1900" max="2025">
            <button class="remove-song"><i class="fas fa-times"></i></button>
        `;
        
        songInputsContainer.appendChild(songInputRow);
        addRemoveSongListener(songInputRow.querySelector('.remove-song'));
    }
    
    /**
     * Adds event listener to remove song button
     * @param {HTMLElement} button - The remove button element
     */
    function addRemoveSongListener(button) {
        button.addEventListener('click', (e) => {
            const songRow = e.target.closest('.song-input-row');
            
            // Only remove if there's more than one song input
            if (document.querySelectorAll('.song-input-row').length > 1) {
                songRow.remove();
            } else {
                // If it's the last one, just clear the inputs
                songRow.querySelector('.song-name').value = '';
                songRow.querySelector('.song-year').value = '';
            }
        });
    }
    
    /**
     * Updates the slider position and active state
     * @param {HTMLElement} option - The clicked slider option
     * @param {number} index - The index of the clicked option
     */
    function updateSlider(option, index) {
        // Remove active class from all options
        sliderOptions.forEach(opt => opt.classList.remove('active'));
        
        // Add active class to clicked option
        option.classList.add('active');
        
        // Move highlight
        sliderHighlight.style.left = `${index * 33.333}%`;
        
        // Update recommendation type
        recommendationType = option.dataset.value;
        
        // Update description
        recommendationDescription.textContent = descriptions[recommendationType];
        
        // Update recommendations container visibility based on type
        if (recommendationType === 'both') {
            document.querySelector('.quick-recommendations').style.display = 'block';
            document.querySelector('.advanced-recommendations').style.display = 'block';
        } else if (recommendationType === 'quick') {
            document.querySelector('.quick-recommendations').style.display = 'block';
            document.querySelector('.advanced-recommendations').style.display = 'none';
        } else {
            document.querySelector('.quick-recommendations').style.display = 'none';
            document.querySelector('.advanced-recommendations').style.display = 'block';
        }
    }
    
    /**
     * Collects song inputs and sends request to get recommendations
     */
    async function getRecommendations() {
        // Clear previous results and errors
        hideError();
        clearRecommendations();
        
        // Get all song inputs
        const songInputRows = document.querySelectorAll('.song-input-row');
        const songs = [];
        
        // Validate and collect song inputs
        let isValid = true;
        
        songInputRows.forEach(row => {
            const nameInput = row.querySelector('.song-name');
            const yearInput = row.querySelector('.song-year');
            
            const name = nameInput.value.trim();
            const year = yearInput.value.trim();
            
            if (name === '') {
                nameInput.style.borderColor = 'var(--error-color)';
                isValid = false;
            } else {
                nameInput.style.borderColor = '';
            }
            
            if (year === '') {
                yearInput.style.borderColor = 'var(--error-color)';
                isValid = false;
            } else {
                yearInput.style.borderColor = '';
            }
            
            if (name !== '' && year !== '') {
                songs.push({
                    name: name,
                    year: parseInt(year)
                });
            }
        });
        
        if (!isValid) {
            showError('Please fill in all song fields');
            return;
        }
        
        if (songs.length === 0) {
            showError('Please add at least one song');
            return;
        }
        
        // Show loader
        loader.classList.remove('hidden');
        recommendationsContainer.classList.add('hidden');
        
        try {
            // Send request to the recommendation API
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    songs: songs,
                    recommendation_type: recommendationType
                })
            });
            
            const data = await response.json();
            
            // Hide loader
            loader.classList.add('hidden');
            
            // Check for errors
            if (!response.ok) {
                showError(data.error || 'Failed to get recommendations');
                return;
            }
            
            // Process and display recommendations
            displayRecommendations(data);
            
        } catch (error) {
            console.error('Error:', error);
            loader.classList.add('hidden');
            showError('An error occurred while fetching recommendations');
        }
    }
    
    /**
     * Displays recommendations in the UI
     * @param {Object} data - The recommendation data
     */
    function displayRecommendations(data) {
        recommendationsContainer.classList.remove('hidden');
        
        // Display quick recommendations if available
        if (data.quick && recommendationType !== 'advanced') {
            if (!data.quick.success) {
                const errorElement = document.createElement('div');
                errorElement.className = 'recommendation-error';
                errorElement.textContent = data.quick.error_message || 'Failed to get quick recommendations';
                quickRecommendationsList.appendChild(errorElement);
            } else if (data.quick.data.length === 0) {
                const noResultsElement = document.createElement('div');
                noResultsElement.className = 'no-results';
                noResultsElement.textContent = 'No matching songs found';
                quickRecommendationsList.appendChild(noResultsElement);
            } else {
                data.quick.data.forEach(song => {
                    const li = createSongElement(song);
                    quickRecommendationsList.appendChild(li);
                });
            }
        }
        
        // Display advanced recommendations if available
        if (data.advanced && recommendationType !== 'quick') {
            if (!data.advanced.success) {
                const errorElement = document.createElement('div');
                errorElement.className = 'recommendation-error';
                errorElement.textContent = data.advanced.error_message || 'Failed to get advanced recommendations';
                advancedRecommendationsList.appendChild(errorElement);
            } else if (data.advanced.data.length === 0) {
                const noResultsElement = document.createElement('div');
                noResultsElement.className = 'no-results';
                noResultsElement.textContent = 'No matching songs found';
                advancedRecommendationsList.appendChild(noResultsElement);
            } else {
                data.advanced.data.forEach(song => {
                    const li = createSongElement(song);
                    advancedRecommendationsList.appendChild(li);
                });
            }
        }
    }
    
    /**
     * Creates a song element for the recommendations list
     * @param {Object} song - The song data
     * @returns {HTMLElement} The song list item element
     */
    function createSongElement(song) {
        const li = document.createElement('li');
        li.className = 'recommendation-item';
        
        // Format artists
        let artists = song.artists;
        if (typeof artists === 'string') {
            // Remove brackets and quotes if present
            artists = artists.replace(/[\[\]']/g, '');
        } else if (Array.isArray(artists)) {
            artists = artists.join(', ');
        }
        
        li.innerHTML = `
            <div class="song-title">${song.name}</div>
            <div class="song-artist">${artists}</div>
            <div class="song-year">${song.year}</div>
        `;
        
        return li;
    }
    
    /**
     * Shows an error message
     * @param {string} message - The error message to display
     */
    function showError(message) {
        errorMessageText.textContent = message;
        errorMessage.classList.remove('hidden');
    }
    
    /**
     * Hides the error message
     */
    function hideError() {
        errorMessage.classList.add('hidden');
    }
    
    /**
     * Clears all recommendation lists
     */
    function clearRecommendations() {
        quickRecommendationsList.innerHTML = '';
        advancedRecommendationsList.innerHTML = '';
    }
}); 