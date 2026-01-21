const labels = JSON.parse(document.getElementById("activity-labels").textContent);
const counts = JSON.parse(document.getElementById("activity-counts").textContent);

new Chart(document.getElementById("activityChart"), {
  type: "doughnut",
  data: {
    labels: labels,
    datasets: [{
      data: counts,
      backgroundColor: ["#16a34a", "#eab308", "#dc2626"]
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: "bottom" }
    }
  }
});
