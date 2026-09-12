// =====================================================
// AGRILINK AI - FRONTEND JAVASCRIPT
// Connects Frontend to Flask Backend
// =====================================================

const API_URL = "http://127.0.0.1:5000";


// =====================================================
// HELPER FUNCTION
// =====================================================

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({
        behavior: "smooth"
    });
}


async function apiRequest(endpoint, method = "GET", data = null) {

    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (data !== null) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(
        `${API_URL}${endpoint}`,
        options
    );

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Something went wrong.");
    }

    return result;
}


// =====================================================
// FARMER REGISTRATION
// =====================================================

async function registerFarmer() {

    const name =
        document.getElementById("farmerName").value;

    const phone =
        document.getElementById("farmerPhone").value;

    const location =
        document.getElementById("farmerLocation").value;

    const resultElement =
        document.getElementById("farmerResult");

    try {

        const result = await apiRequest(
            "/farmers",
            "POST",
            {
                name: name,
                phone: phone,
                location: location
            }
        );

        resultElement.innerHTML =
            `✅ Farmer registered successfully!<br>
             Farmer ID: ${result.farmer_id}`;

    } catch (error) {

        resultElement.innerHTML =
            `❌ ${error.message}`;
    }
}


// =====================================================
// PRODUCE REGISTRATION
// =====================================================

async function registerProduce() {

    const farmerId =
        document.getElementById("produceFarmerId").value;

    const cropName =
        document.getElementById("cropName").value;

    const quantity =
        document.getElementById("quantity").value;

    const location =
        document.getElementById("produceLocation").value;

    const availabilityDate =
        document.getElementById("availabilityDate").value;

    const resultElement =
        document.getElementById("produceResult");

    try {

        const result = await apiRequest(
            "/produce",
            "POST",
            {
                farmer_id: Number(farmerId),
                crop_name: cropName,
                quantity_kg: Number(quantity),
                location: location,
                availability_date: availabilityDate
            }
        );

        resultElement.innerHTML =
            `✅ Produce registered successfully!<br>
             Produce ID: ${result.produce_id}`;

    } catch (error) {

        resultElement.innerHTML =
            `❌ ${error.message}`;
    }
}


// =====================================================
// CREATE SMART POOL
// =====================================================

async function createPool() {

    const crop =
        document.getElementById("poolCrop").value;

    const location =
        document.getElementById("poolLocation").value;

    const resultElement =
        document.getElementById("poolResult");

    try {

        const result = await apiRequest(
            "/pools",
            "POST",
            {
                crop_name: crop,
                location: location
            }
        );

        resultElement.innerHTML =
            `✅ Pool created successfully!<br>
             Pool ID: ${result.pool_id}`;

    } catch (error) {

        resultElement.innerHTML =
            `❌ ${error.message}`;
    }
}


// =====================================================
// BUYER REGISTRATION
// =====================================================

async function registerBuyer() {

    const buyerName =
        document.getElementById("buyerName").value;

    const crop =
        document.getElementById("buyerCrop").value;

    const quantity =
        document.getElementById("buyerQuantity").value;

    const location =
        document.getElementById("buyerLocation").value;

    const urgency =
        document.getElementById("buyerUrgency").value;

    const resultElement =
        document.getElementById("buyerResult");

    try {

        const result = await apiRequest(
            "/buyers",
            "POST",
            {
                buyer_name: buyerName,
                crop_name: crop,
                required_quantity_kg: Number(quantity),
                location: location,
                urgency: urgency
            }
        );

        resultElement.innerHTML =
            `✅ Buyer registered successfully!<br>
             Buyer ID: ${result.buyer_id}`;

    } catch (error) {

        resultElement.innerHTML =
            `❌ ${error.message}`;
    }
}


// =====================================================
// SMART MATCHING
// =====================================================

async function getMatchSuggestions() {

    const container =
        document.getElementById("matchResults");

    container.innerHTML =
        "<p>🤖 AgriLink AI is finding suitable matches...</p>";

    try {

        const result = await apiRequest(
            "/matches/suggestions"
        );

        if (result.count === 0) {

            container.innerHTML =
                "<p>No suitable matches found yet.</p>";

            return;
        }

        let html = "";

        result.suggestions.forEach((suggestion, index) => {

            html += `
                <div class="result-card">

                    <h3>
                        🤖 Match ${index + 1}
                    </h3>

                    <p>
                        <strong>Match Score:</strong>
                        ${suggestion.match_score}%
                    </p>

                    <p>
                        <strong>Quantity Difference:</strong>
                        ${suggestion.quantity_difference_kg} KG
                    </p>

                    <p>
                        <strong>Pool:</strong>
                        ${suggestion.pool.crop_name}
                        -
                        ${suggestion.pool.total_quantity_kg} KG
                    </p>

                    <p>
                        <strong>Buyer:</strong>
                        ${suggestion.buyer.buyer_name}
                    </p>

                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {

        container.innerHTML =
            `<p>❌ ${error.message}</p>`;
    }
}


// =====================================================
// JOURNEY TRACKING
// =====================================================

async function trackJourney() {

    const matchId =
        document.getElementById("journeyId").value;

    const container =
        document.getElementById("journeyResults");

    try {

        const result = await apiRequest(
            `/journey/match/${matchId}`
        );

        if (!result.journey ||
            result.journey.length === 0) {

            container.innerHTML =
                "<p>No journey information found.</p>";

            return;
        }

        let html =
            "<div class='result-card'><h3>📍 Journey Timeline</h3>";

        result.journey.forEach((step) => {

            html += `
                <p>
                    ✅ <strong>
                    ${step.current_status}
                    </strong>
                    <br>
                    <small>
                    ${step.timestamp}
                    </small>
                </p>
                <br>
            `;
        });

        html += "</div>";

        container.innerHTML = html;

    } catch (error) {

        container.innerHTML =
            `<p>❌ ${error.message}</p>`;
    }
}
// =====================================================
// AI MARKET PRICE PREDICTION
// =====================================================

async function predictMarketPrice() {

    const year =
        document.getElementById("predictionYear").value;

    const month =
        document.getElementById("predictionMonth").value;

    const day =
        document.getElementById("predictionDay").value;

    const arrivalQuantity =
        document.getElementById("predictionArrival").value;

    const minPrice =
        document.getElementById("predictionMinPrice").value;

    const maxPrice =
        document.getElementById("predictionMaxPrice").value;

    const previousModalPrice =
        document.getElementById(
            "predictionPreviousPrice"
        ).value;

    const resultElement =
        document.getElementById("predictionResult");


    resultElement.innerHTML =
        "<p>🤖 AgriLink AI is predicting the market price...</p>";


    try {

        const result = await apiRequest(
            "/predict-price",
            "POST",
            {
                year: Number(year),
                month: Number(month),
                day: Number(day),
                arrival_quantity: Number(arrivalQuantity),
                min_price: Number(minPrice),
                max_price: Number(maxPrice),
                previous_modal_price: Number(previousModalPrice)
            }
        );


        resultElement.innerHTML = `

            <div class="result-card">

                <h3>📈 Predicted Market Price</h3>

                <h1>
                    ₹${Number(
                        result.predicted_modal_price
                    ).toFixed(2)}
                </h1>

                <p>
                    🤖 AI prediction based on
                    historical market data.
                </p>

            </div>

        `;

    } catch (error) {

        resultElement.innerHTML =
            `<p>❌ ${error.message}</p>`;

    }
}