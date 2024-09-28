document.getElementById('downloadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const url = document.getElementById('url').value;
    const format = document.getElementById('outputFormat').value;
    const downloadURL = 'https://youtube-to-mp3-or-mp4-website.onrender.com/download'

    // Here, you would call your backend API
    const response = await fetch(downloadURL, {
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
