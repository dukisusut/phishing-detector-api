// =====================================================
// REALTIME PHISHING DETECTION
// =====================================================

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {

    // =================================================
    // CHI CHAY KHI LOAD XONG
    // =================================================

    if (changeInfo.status !== "complete") {
        return;
    }

    // =================================================
    // LAY URL
    // =================================================

    const url = tab.url;

    if (!url) {
        return;
    }

    // =================================================
    // BO QUA TRANG NOI BO CHROME
    // =================================================

    if (
        url.startsWith("chrome://") ||
        url.startsWith("edge://") ||
        url.startsWith("about:")
    ) {
        return;
    }

    console.log("[SCAN]", url);

    try {

        // =============================================
        // GOI API BACKEND
        // =============================================

        const response = await fetch(
            "http://127.0.0.1:8000/predict-url",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: url
                })
            }
        );

        const data = await response.json();

        console.log("[RESULT]", data);

        // =============================================
        // NEU KHONG PHISHING
        // =============================================

        if (!data.is_phishing) {
            return;
        }

        // =============================================
        // SHOW NOTIFICATION
        // =============================================

        chrome.notifications.create({
            type: "basic",
            iconUrl: "icon.png",
            title: "Phishing Warning",
            message: "Dangerous phishing website detected!"
        });

        // =============================================
        // INJECT WARNING OVERLAY
        // =============================================

        await chrome.scripting.executeScript({
            target: {
                tabId: tabId
            },

            func: () => {

                // =====================================
                // TRANH INJECT NHIEU LAN
                // =====================================

                if (document.getElementById("phishing-warning")) {
                    return;
                }

                // =====================================
                // TAO OVERLAY
                // =====================================

                const overlay = document.createElement("div");

                overlay.id = "phishing-warning";

                overlay.style.position = "fixed";
                overlay.style.top = "0";
                overlay.style.left = "0";
                overlay.style.width = "100vw";
                overlay.style.height = "100vh";
                overlay.style.background = "rgba(255,0,0,0.96)";
                overlay.style.zIndex = "999999999";
                overlay.style.display = "flex";
                overlay.style.flexDirection = "column";
                overlay.style.justifyContent = "center";
                overlay.style.alignItems = "center";
                overlay.style.color = "white";
                overlay.style.fontFamily = "Arial";
                overlay.style.textAlign = "center";

                overlay.innerHTML = `
                    <div style="font-size:48px;font-weight:bold;">
                        ⚠️ PHISHING WEBSITE DETECTED
                    </div>

                    <div style="font-size:22px;margin-top:20px;">
                        This website may steal your password,
                        account or payment information.
                    </div>

                    <button id="close-warning"
                        style="
                            margin-top:40px;
                            padding:15px 30px;
                            font-size:20px;
                            border:none;
                            border-radius:10px;
                            cursor:pointer;
                        ">
                        Continue Anyway
                    </button>
                `;

                document.documentElement.appendChild(overlay);

                // =====================================
                // BUTTON CLOSE
                // =====================================

                document
                    .getElementById("close-warning")
                    .onclick = () => {

                        overlay.remove();
                    };
            }
        });

    } catch (err) {

        console.log("[ERROR]", err);
    }
});
