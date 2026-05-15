document.getElementById("checkBtn").addEventListener("click", async () => {

    const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    const url = tab.url;

    console.log("Current URL:", url);

    const response = await fetch("http://127.0.0.1:8000/predict-url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: url
        })
    });

    const data = await response.json();

    console.log(data);

    const resultDiv = document.getElementById("result");

    if (data.is_phishing) {
        resultDiv.innerHTML =
            " PHISHING DETECTED<br>" +
            "Confidence: " + data.confidence;
    } else {
        resultDiv.innerHTML =
            " Safe Website";
    }
});
