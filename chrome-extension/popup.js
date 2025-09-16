document.getElementById("check").addEventListener("click", () => {
  const comment = document.getElementById("comment").value;
  const resultDiv = document.getElementById("result");
  const loadingDiv = document.getElementById("loading");

  resultDiv.innerHTML = "";               // Clear result
  loadingDiv.classList.remove("hidden"); // Show loading

  if (!comment) {
    resultDiv.innerHTML = "⚠️ Please enter a comment.";
    loadingDiv.classList.add("hidden");
    return;
  }


  fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ comment: comment })
  })
    .then(response => response.json())
    .then(data => {
      loadingDiv.classList.add("hidden"); // Hide loading

      const confidencePercent = Math.round(data.confidence * 100);
      const confidenceColor = data.confidence >= 0.8 ? "#2ecc71" :
                              data.confidence >= 0.5 ? "#f1c40f" : "#e74c3c";
      
      resultDiv.innerHTML = `
      ${data.is_bot === 1 
        ? `<span class="bot">🤖 This might be a BOT!</span>` 
        : `<span class="valid">✅ Valid comment</span>`}
      <div id="confidence-bar">
        <div id="confidence-fill" style="width: ${confidencePercent}%; background-color: ${confidenceColor};"></div>
      </div>
      <div>Confidence: ${confidencePercent}%</div>
    `;

    })
    .catch(err => {
      loadingDiv.classList.add("hidden");
      resultDiv.textContent = "❌ Error connecting to API";
      console.error(err);
    });
});

document.getElementById("comment").addEventListener("input", () => {
  document.getElementById("result").innerHTML = "";
});

document.getElementById("darkToggle").addEventListener("change", (e) => {
  document.body.classList.toggle("dark", e.target.checked);
});


