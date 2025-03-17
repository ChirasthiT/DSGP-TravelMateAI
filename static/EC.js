window.onload = function () {
    fetchRecommendations();
};

async function fetchRecommendations() {
    try {
        document.getElementById('loading-spinner').style.display = 'block';
        document.getElementById('loading-spinner2').style.display = 'block';
        document.getElementById('recommendation').innerHTML = '';
        document.getElementById('recommendation2').innerHTML = '';

        const url = `http://127.0.0.1:5000/recommendation/recommend` ;
        const response = await fetch(url);
        console.log("Fetching recommendations...");

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        if (!data.CBrecommendations || data.CBrecommendations.length === 0) {
            throw new Error("No recommendations found.");
        }
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('loading-spinner2').style.display = 'none';

        console.log("CB-",data.CBrecommendations)
        console.log("IBC-",data.IBCrecommendations)


         // Merge recommendations while removing duplicates
        const uniqueRecommendations = new Map();

        // Add content-based recommendations
        data.CBrecommendations.forEach(item => {
            uniqueRecommendations.set(item.Name.toLowerCase(), item);
        });

        // Add item-based recommendations (only if they don't already exist)
        data.IBCrecommendations.forEach(item => {
            if (!uniqueRecommendations.has(item.Name.toLowerCase())) {
                uniqueRecommendations.set(item.Name.toLowerCase(), item);
            }
        });

        const finalRecommendations = Array.from(uniqueRecommendations.values()).sort((a, b) => b.Rating - a.Rating);

       // Separate accommodations and restaurants
        const accommodations = finalRecommendations
            .filter(item => item.Source.toLowerCase() === "accomodation")
            .slice(0, 15);

        const restaurants = finalRecommendations
            .filter(item => item.Source.toLowerCase() === "restaurant")
            .slice(0, 15);

        renderRecommendations(accommodations, 'recommendation');
        renderRecommendations(restaurants, 'recommendation2');


        // Reinitialize Owl Carousel after content is added
        $(".rec-carousel").owlCarousel({
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

function renderRecommendations(recommendations, containerId) {
    const recommendationDiv = document.getElementById(containerId);
    recommendationDiv.innerHTML = '';

    recommendations.forEach((item) => {
        const recommendationItem = document.createElement('div');
        recommendationItem.className = 'rec-item bg-white text-center border p-4';
        recommendationItem.style.cursor = "pointer";

        const imgSrc = item.Image ? `data:image/jpeg;base64,${item.Image}` : 'default-image.jpg';

        recommendationItem.innerHTML = `
            <img class="bg-white no-bg rounded shadow p-1 mx-auto mb-3" src="${imgSrc}" style="width: 120px; height: 120px; object-fit: cover;">
            <h5 class="mb-2">${item.Name.toUpperCase()}</h5>
            <p><i class="fa fa-map-marker-alt me-3"></i>${item.Address || 'No address provided'}</p>
            <p><strong>Rating:</strong> ${item.Rating ? getStarRating(item.Rating) : 'Not rated'}</p>
        `;

        recommendationItem.onclick = function () {
            console.log(item);
            openModal(item);
            logClick(item)
        };


        recommendationDiv.appendChild(recommendationItem);
    });
}

function logClick(item) {

        const budgetMapping = {
            1: 'Low',
            2: 'Medium',
            3: 'High'
        };
        const budgetLabel = budgetMapping[item['Budget Level']] || 'unknown';
        fetch('http://127.0.0.1:5000/recommendation/log_click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "name": item.Name,
                "district": item.District,
                "budget": budgetLabel,

            })
        })
        .then(response => response.json())
        .then(data => console.log("Click logged:", data))
        .catch(error => console.error("Error logging click:", error));
    }

function openModal(item) {
    document.getElementById("modal-image").src = item.Image ? `data:image/jpeg;base64,${item.Image}` : 'default-image.jpg';
    document.getElementById("modal-title").textContent = item.Name.toUpperCase();
    document.getElementById("modal-address").textContent = item.Address || "No address provided";
    document.getElementById("modal-rating").innerHTML = item.Rating ? getStarRating(item.Rating) : 'Not rated';

    document.getElementById("recommendation-modal").style.display = "block";
}

// Function to close the modal
function closeModal() {
    document.getElementById("recommendation-modal").style.display = "none";
}

function getStarRating(rating) {
    const maxStars = 5;
    const fullStar = "★";
    const halfStar = "☆";
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
