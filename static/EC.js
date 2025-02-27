document.addEventListener("DOMContentLoaded", function () {
    fetchRecommendations();
});

async function fetchRecommendations() {
    try {

        const url = `http://127.0.0.1:5000/recommendation/recommend` ;
        const response = await fetch(url);
        console.log("Fetching recommendations...");

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        if (!data.recommendations || data.recommendations.length === 0) {
            throw new Error("No recommendations found.");
        }

        renderRecommendations(data.recommendations);

        // Reinitialize Owl Carousel after content is added
        $(".recommendation-carousel").owlCarousel({
            autoplay: true,
            smartSpeed: 1000,
            center: true,
            margin: 24,
            dots: true,
            loop: true,
            nav : false,
            responsive: {
                0:{
                    items:1
                },
                768:{
                    items:2
                },
                992:{
                    items:3
                }
            }
        });

    } catch (error) {
        console.error(error);
        document.getElementById('recommendation').innerHTML =
            `<div class="alert alert-danger">${error.message}</div>`;
    }
}

function renderRecommendations(recommendations) {
    const recommendationDiv = document.getElementById('recommendation');
    recommendationDiv.innerHTML = '';

    recommendations.forEach((item) => {
        const recommendationItem = document.createElement('div');
        recommendationItem.className = 'recommendation-item bg-white text-center border p-4';

        const imgSrc = item.Image ? `data:image/jpeg;base64,${item.Image}` : 'default-image.jpg';

        recommendationItem.innerHTML = `
            <img class="bg-white rounded shadow p-1 mx-auto mb-3" src="${imgSrc}" style="width: 120px; height: 120px; object-fit: cover;">
            <h5 class="mb-2">${item.Name}</h5>
            <p>${item.Address || 'No address provided'}</p>
            <p><strong>Rating:</strong> ${item.Rating ? getStarRating(item.Rating) : 'Not rated'}</p>
        `;

        recommendationDiv.appendChild(recommendationItem);
    });
}

function getStarRating(rating) {
    const maxStars = 5;
    const fullStar = "★";
    const halfStar = "½";
    const emptyStar = "☆";

    let stars = "";
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating - fullStars >= 0.5;

    for (let i = 0; i < fullStars; i++) {
        stars += fullStar;
    }
    if (hasHalfStar) {
        stars += halfStar;
    }
    const remainingStars = maxStars - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < remainingStars; i++) {
        stars += emptyStar;
    }
    return `<span style="color: gold;">${stars}</span>`;
}
