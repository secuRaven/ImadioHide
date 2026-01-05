function showSection(sectionId) {
    // Hide all sections first
    document.querySelectorAll('.section-content').forEach(section => {
        section.style.display = 'none';
        // Clear any previous status or messages when hiding
        const statusElement = section.querySelector('.status-message');
        if (statusElement) statusElement.textContent = '';
        const decodedMessageElement = section.querySelector('.decoded-message');
        if (decodedMessageElement) decodedMessageElement.textContent = '';
    });

    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
}

async function uploadFile(type, action) {
    const fileInput = document.getElementById(`${type}${action.charAt(0).toUpperCase() + action.slice(1)}Input`);
    const messageInput = document.getElementById(`${type}${action.charAt(0).toUpperCase() + action.slice(1)}Message`);
    const outputNameInput = document.getElementById(`${type}${action.charAt(0).toUpperCase() + action.slice(1)}OutputName`);
    const statusElement = document.getElementById(`${type}${action.charAt(0).toUpperCase() + action.slice(1)}Status`);
    const decodedMessageElement = document.getElementById(`${type}DecodedMessage`);

    statusElement.className = 'status-message'; // Reset classes
    statusElement.textContent = 'Processing...';

    const file = fileInput.files[0];
    if (!file) {
        statusElement.textContent = 'Please select a file.';
        statusElement.classList.add('error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    formData.append('action', action);

    if (action === 'encode') {
        const secretMessage = messageInput.value.trim();
        const outputFilename = outputNameInput.value.trim();
        if (!secretMessage) {
            statusElement.textContent = 'Please enter a secret message.';
            statusElement.classList.add('error');
            return;
        }
        if (!outputFilename) {
            statusElement.textContent = 'Please enter an output filename.';
            statusElement.classList.add('error');
            return;
        }
        formData.append('message', secretMessage);
        formData.append('output_name', outputFilename);
    }

    try {
        // --- IMPORTANT: This is a placeholder for your actual API call ---
        // You would replace this with a fetch request to your Python backend
        // Example: const response = await fetch('/api/stego-process', { method: 'POST', body: formData });
        // For demonstration, we'll simulate a delay and a response.

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2000)); 

        // Simulate success or failure
        const success = Math.random() > 0.2; // 80% chance of success for demo

        if (success) {
            statusElement.textContent = `Successfully ${action}d ${file.name}.`;
            statusElement.classList.add('success');

            if (action === 'decode' && decodedMessageElement) {
                // Simulate decoded message
                decodedMessageElement.textContent = `Decoded message: "This is a secret message hidden in the ${type} file!"`;
            } else if (action === 'encode') {
                // In a real app, the backend would return a URL to download the stego file.
                // For demo, we just indicate success.
            }
        } else {
            statusElement.textContent = `Failed to ${action} ${file.name}. Please try again.`;
            statusElement.classList.add('error');
            if (decodedMessageElement) decodedMessageElement.textContent = '';
        }

    } catch (error) {
        statusElement.textContent = `An error occurred: ${error.message}`;
        statusElement.classList.add('error');
        console.error('Frontend error:', error);
        if (decodedMessageElement) decodedMessageElement.textContent = '';
    }
}