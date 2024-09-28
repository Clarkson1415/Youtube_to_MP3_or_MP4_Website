document.getElementById('downloadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const url = document.getElementById('url').value;
    const format = document.getElementById('outputFormat').value;

    // Here, you would call your backend API
    const response = await fetch('http://127.0.0.1:5000/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url, format })
    });

    const data = await response.json();
    
    // Handle the response
    if (data.success) {
        document.getElementById('message').innerText = "Download started!";
    } else {
        document.getElementById('message').innerText = "Error: " + data.error;
    }
});
