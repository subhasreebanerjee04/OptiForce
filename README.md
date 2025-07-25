# OptiForce - Workforce Cost Optimizer

OPTIFORCE is a user-friendly Flask web application for workforce cost optimization. It leverages LLM features to help organizations optimize hiring strategies across global markets, enabling significant cost savings and operational efficiency.

## Features:

1. Cost analysis incorporating geographic cost indices, social charges, benefits and contractor premiums.
2. Multi-scenario optimization: Most Cost-Effective Mix, Balanced Approach and Current Strategy.
3. AI-powered, plain-language insights generated by a lightweight Large Language Model (LLM).
4. Interactive dashboard with dynamic charts (Chart.js), scenario comparisons and savings calculators.

## Technology Stack:

1. Python 3
2. Flask web framework
3. JavaScript (ES6) for frontend interactivity
4. Chart.js for data visualization
5. Lightweight LLM integration using Hugging Face Transformers (Microsoft Phi-3 model)

## Installation:

git clone https://github.com/yourusername/optiforce.git
cd optiforce

(OPTIONAL)
python -m venv venv
### On Windows:
venv\Scripts\activate
### On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

## Usage:

python optiforce_app.py

## Project Structure:



## API Endpoints:

1. / : Serves the main web page.
2. /api/optimize : POST endpoint to receive workforce parameters and return optimization scenarios and AI insights.
3. /api/llm-explain : POST endpoint for generating LLM-based explanations.
4. /api/cost-calculator : POST endpoint for real-time cost calculations.
5. /api/locations : GET endpoint to retrieve available locations.
6. /api/job-roles : GET endpoint to retrieve available job roles.

## Deployment:

gunicorn optiforce_app:app

## License:

This project is licensed under the MIT License.

*Contributions are welcome! Please fork the repository and submit pull requests for improvements or bug fixes.*


