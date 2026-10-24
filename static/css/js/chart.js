function drawChart(pos, neg, neu) {
    const ctx = document.getElementById("chart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Positive", "Negative", "Neutral"],
            datasets: [{
                label: "Sentiment Count",
                data: [pos, neg, neu]
            }]
        }
    });
}
const caption = prompt("Enter caption for sentiment analysis:");

fetch("/analyze_instagram", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: caption })
})