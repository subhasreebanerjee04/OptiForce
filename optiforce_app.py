
from flask import Flask, render_template, request, jsonify
import json
import random
import time
from typing import Dict, List, Any
import math
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os



app = Flask(__name__)

# ============================================================================
# PHASE 1: DATA INGESTION SERVICE
# ============================================================================

class DataIngestionService:
    """Phase 1: Handles real-time salary, benefits, and geographic cost data"""

    def __init__(self):
        self.job_roles = [
            {"id": "software-engineer", "name": "Software Engineer", "baseMultiplier": 1.0},
            {"id": "data-scientist", "name": "Data Scientist", "baseMultiplier": 1.2},
            {"id": "product-manager", "name": "Product Manager", "baseMultiplier": 1.1},
            {"id": "devops-engineer", "name": "DevOps Engineer", "baseMultiplier": 1.05},
            {"id": "ui-ux-designer", "name": "UI/UX Designer", "baseMultiplier": 0.9},
            {"id": "marketing-manager", "name": "Marketing Manager", "baseMultiplier": 0.95},
            {"id": "sales-manager", "name": "Sales Manager", "baseMultiplier": 1.0},
            {"id": "hr-manager", "name": "HR Manager", "baseMultiplier": 0.85}
        ]

        self.locations = [
            {"id": "usa", "name": "USA", "costIndex": 1.0, "socialCharges": 0.12, "benefits": 0.25, "contractorPremium": 2.0},
            {"id": "germany", "name": "Germany", "costIndex": 0.85, "socialCharges": 0.45, "benefits": 0.22, "contractorPremium": 1.8},
            {"id": "india", "name": "India", "costIndex": 0.25, "socialCharges": 0.12, "benefits": 0.08, "contractorPremium": 1.2},
            {"id": "portugal", "name": "Portugal", "costIndex": 0.55, "socialCharges": 0.23, "benefits": 0.15, "contractorPremium": 1.5},
            {"id": "poland", "name": "Poland", "costIndex": 0.45, "socialCharges": 0.35, "benefits": 0.18, "contractorPremium": 1.4},
            {"id": "ukraine", "name": "Ukraine", "costIndex": 0.30, "socialCharges": 0.22, "benefits": 0.12, "contractorPremium": 1.3},
            {"id": "philippines", "name": "Philippines", "costIndex": 0.20, "socialCharges": 0.15, "benefits": 0.10, "contractorPremium": 1.2},
            {"id": "mexico", "name": "Mexico", "costIndex": 0.35, "socialCharges": 0.28, "benefits": 0.16, "contractorPremium": 1.4}
        ]

        self.base_salaries = {
            "software-engineer": 95000,
            "data-scientist": 110000,
            "product-manager": 105000,
            "devops-engineer": 100000,
            "ui-ux-designer": 85000,
            "marketing-manager": 90000,
            "sales-manager": 95000,
            "hr-manager": 80000
        }

        



    def get_salary_data(self, job_role: str, location: str) -> Dict[str, Any]:
        """Simulate real-time salary data fetching with geographic adjustments"""
        location_data = next((loc for loc in self.locations if loc["id"] == location), None)
        job_data = next((job for job in self.job_roles if job["id"] == job_role), None)

        if not location_data or not job_data:
            raise ValueError("Invalid job role or location")

        base_salary = self.base_salaries[job_role]
        adjusted_salary = base_salary * job_data["baseMultiplier"] * location_data["costIndex"]

        return {
            "base_salary": adjusted_salary,
            "location_data": location_data,
            "job_data": job_data,
            "social_charges_rate": location_data["socialCharges"],
            "benefits_rate": location_data["benefits"],
            "contractor_premium": location_data["contractorPremium"]
        }

# ============================================================================
# PHASE 2: OPTIMIZATION ENGINE
# ============================================================================

'''class OptimizationEngine:
    """Phase 2: Generates cost-optimized workforce scenarios"""

    def __init__(self, data_service: DataIngestionService):
        self.data_service = data_service

    def calculate_fte_cost(self, job_role: str, location: str) -> Dict[str, float]:
        """Calculate full-time employee total cost"""
        salary_data = self.data_service.get_salary_data(job_role, location)

        base_salary = salary_data["base_salary"]
        social_charges = base_salary * salary_data["social_charges_rate"]
        benefits = base_salary * salary_data["benefits_rate"]
        total_cost = base_salary + social_charges + benefits

        return {
            "base_salary": base_salary,
            "social_charges": social_charges,
            "benefits": benefits,
            "total_cost": total_cost,
            "type": "FTE"
        }

    def calculate_contractor_cost(self, job_role: str, location: str) -> Dict[str, float]:
        """Calculate contractor total cost"""
        salary_data = self.data_service.get_salary_data(job_role, location)

        base_salary = salary_data["base_salary"]
        contractor_rate = base_salary * salary_data["contractor_premium"]
        # Contractors typically have reduced benefits and social charges
        social_charges = contractor_rate * 0.05  # Minimal social charges
        benefits = 0  # No benefits for contractors
        total_cost = contractor_rate + social_charges

        return {
            "base_salary": contractor_rate,
            "social_charges": social_charges,
            "benefits": benefits,
            "total_cost": total_cost,
            "type": "Contractor"
        }

    def generate_scenarios(self, job_role: str, primary_location: str, headcount: int, constraint: str) -> Dict[str, Any]:
        """Generate three optimization scenarios"""
        scenarios = {}

        # Most Cost-Effective Mix
        scenarios["cost_effective"] = self._generate_cost_effective_scenario(job_role, headcount)

        # Balanced Approach
        scenarios["balanced"] = self._generate_balanced_scenario(job_role, headcount)

        # Current Strategy (baseline)
        scenarios["current"] = self._generate_current_scenario(job_role, primary_location, headcount)

        return scenarios

    def _generate_cost_effective_scenario(self, job_role: str, headcount: int) -> Dict[str, Any]:
        """Generate the most cost-effective workforce mix"""
        # Prioritize lowest cost locations and contractor mix
        cost_locations = ["india", "philippines", "ukraine"]

        allocation = []
        total_cost = 0

        # 70% contractors in lowest cost location, 30% FTE in second lowest
        contractor_count = int(headcount * 0.7)
        fte_count = headcount - contractor_count

        if contractor_count > 0:
            contractor_cost = self.calculate_contractor_cost(job_role, "india")
            allocation.append({
                "location": "India",
                "type": "Contractor",
                "count": contractor_count,
                "unit_cost": contractor_cost["total_cost"],
                "total_cost": contractor_cost["total_cost"] * contractor_count
            })
            total_cost += contractor_cost["total_cost"] * contractor_count

        if fte_count > 0:
            fte_cost = self.calculate_fte_cost(job_role, "philippines")
            allocation.append({
                "location": "Philippines",
                "type": "FTE",
                "count": fte_count,
                "unit_cost": fte_cost["total_cost"],
                "total_cost": fte_cost["total_cost"] * fte_count
            })
            total_cost += fte_cost["total_cost"] * fte_count

        return {
            "name": "Most Cost-Effective Mix",
            "allocation": allocation,
            "total_cost": total_cost,
            "avg_cost_per_employee": total_cost / headcount,
            "description": "Optimized for maximum cost savings"
        }

    def _generate_balanced_scenario(self, job_role: str, headcount: int) -> Dict[str, Any]:
        """Generate balanced approach considering risk and quality"""
        allocation = []
        total_cost = 0

        # 40% India contractors, 35% Portugal FTE, 25% Poland FTE
        india_count = int(headcount * 0.4)
        portugal_count = int(headcount * 0.35)
        poland_count = headcount - india_count - portugal_count

        if india_count > 0:
            contractor_cost = self.calculate_contractor_cost(job_role, "india")
            allocation.append({
                "location": "India",
                "type": "Contractor",
                "count": india_count,
                "unit_cost": contractor_cost["total_cost"],
                "total_cost": contractor_cost["total_cost"] * india_count
            })
            total_cost += contractor_cost["total_cost"] * india_count

        if portugal_count > 0:
            fte_cost = self.calculate_fte_cost(job_role, "portugal")
            allocation.append({
                "location": "Portugal",
                "type": "FTE",
                "count": portugal_count,
                "unit_cost": fte_cost["total_cost"],
                "total_cost": fte_cost["total_cost"] * portugal_count
            })
            total_cost += fte_cost["total_cost"] * portugal_count

        if poland_count > 0:
            fte_cost = self.calculate_fte_cost(job_role, "poland")
            allocation.append({
                "location": "Poland",
                "type": "FTE",
                "count": poland_count,
                "unit_cost": fte_cost["total_cost"],
                "total_cost": fte_cost["total_cost"] * poland_count
            })
            total_cost += fte_cost["total_cost"] * poland_count

        return {
            "name": "Balanced Approach",
            "allocation": allocation,
            "total_cost": total_cost,
            "avg_cost_per_employee": total_cost / headcount,
            "description": "Balances cost, risk, and talent quality"
        }

    def _generate_current_scenario(self, job_role: str, location: str, headcount: int) -> Dict[str, Any]:
        """Generate current strategy baseline"""
        fte_cost = self.calculate_fte_cost(job_role, location)
        total_cost = fte_cost["total_cost"] * headcount

        location_name = next((loc["name"] for loc in self.data_service.locations if loc["id"] == location), location)

        allocation = [{
            "location": location_name,
            "type": "FTE",
            "count": headcount,
            "unit_cost": fte_cost["total_cost"],
            "total_cost": total_cost
        }]

        return {
            "name": "Current Strategy",
            "allocation": allocation,
            "total_cost": total_cost,
            "avg_cost_per_employee": total_cost / headcount,
            "description": "Current baseline approach"
        }'''
class OptimizationEngine:
    def __init__(self, data_service):
        self.data_service = data_service

    def calculate_fte_cost(self, job_role, location, headcount):
        salary_data = self.data_service.get_salary_data(job_role, location)
        base_salary = salary_data["base_salary"]
        social_charges = base_salary * salary_data["social_charges_rate"]
        benefits = base_salary * salary_data["benefits_rate"]
        total_cost = base_salary + social_charges + benefits
        return {
            "base_salary": base_salary,
            "social_charges": social_charges,
            "benefits": benefits,
            "total_cost": total_cost * headcount,
            "type": "FTE"
        }

    def calculate_contractor_cost(self, job_role, location, headcount):
        salary_data = self.data_service.get_salary_data(job_role, location)
        base_salary = salary_data["base_salary"]
        contractor_rate = base_salary * salary_data["contractor_premium"]
        social_charges = contractor_rate * 0.05
        benefits = 0
        total_cost = contractor_rate + social_charges
        return {
            "base_salary": contractor_rate,
            "social_charges": social_charges,
            "benefits": benefits,
            "total_cost": total_cost * headcount,
            "type": "Contractor"
        }

    def generate_scenarios(self, job_role, primary_location, headcount, constraint, employment_type):
        scenarios = {}

        if employment_type == 'both':
            # Example: 70% contractors, 30% FTE for cost-effective
            contractor_count = int(headcount * 0.7)
            fte_count = headcount - contractor_count

            allocation = []
            total_cost = 0

            if contractor_count > 0:
                contractor_cost = self.calculate_contractor_cost(job_role, "india", contractor_count)
                allocation.append({
                    "location": "India",
                    "type": "Contractor",
                    "count": contractor_count,
                    "unit_cost": contractor_cost["total_cost"] / contractor_count,
                    "total_cost": contractor_cost["total_cost"]
                })
                total_cost += contractor_cost["total_cost"]

            if fte_count > 0:
                fte_cost = self.calculate_fte_cost(job_role, "philippines", fte_count)
                allocation.append({
                    "location": "Philippines",
                    "type": "FTE",
                    "count": fte_count,
                    "unit_cost": fte_cost["total_cost"] / fte_count,
                    "total_cost": fte_cost["total_cost"]
                })
                total_cost += fte_cost["total_cost"]

            scenarios["cost_effective"] = {
                "name": "Most Cost-Effective Mix",
                "allocation": allocation,
                "total_cost": total_cost,
                "avg_cost_per_employee": total_cost / headcount,
                "description": "Optimized for maximum cost savings"
            }

            # Balanced scenario (example: 40% contractors, 60% FTE split)
            india_count = int(headcount * 0.4)
            portugal_count = int(headcount * 0.35)
            poland_count = headcount - india_count - portugal_count

            allocation = []
            total_cost = 0

            if india_count > 0:
                contractor_cost = self.calculate_contractor_cost(job_role, "india", india_count)
                allocation.append({
                    "location": "India",
                    "type": "Contractor",
                    "count": india_count,
                    "unit_cost": contractor_cost["total_cost"] / india_count,
                    "total_cost": contractor_cost["total_cost"]
                })
                total_cost += contractor_cost["total_cost"]

            if portugal_count > 0:
                fte_cost = self.calculate_fte_cost(job_role, "portugal", portugal_count)
                allocation.append({
                    "location": "Portugal",
                    "type": "FTE",
                    "count": portugal_count,
                    "unit_cost": fte_cost["total_cost"] / portugal_count,
                    "total_cost": fte_cost["total_cost"]
                })
                total_cost += fte_cost["total_cost"]

            if poland_count > 0:
                fte_cost = self.calculate_fte_cost(job_role, "poland", poland_count)
                allocation.append({
                    "location": "Poland",
                    "type": "FTE",
                    "count": poland_count,
                    "unit_cost": fte_cost["total_cost"] / poland_count,
                    "total_cost": fte_cost["total_cost"]
                })
                total_cost += fte_cost["total_cost"]

            scenarios["balanced"] = {
                "name": "Balanced Approach",
                "allocation": allocation,
                "total_cost": total_cost,
                "avg_cost_per_employee": total_cost / headcount,
                "description": "Balances cost, risk, and talent quality"
            }

            # Current scenario (all FTE in primary location)
            fte_cost = self.calculate_fte_cost(job_role, primary_location, headcount)
            scenarios["current"] = {
                "name": "Current Strategy",
                "allocation": [{
                    "location": primary_location,
                    "type": "FTE",
                    "count": headcount,
                    "unit_cost": fte_cost["total_cost"] / headcount,
                    "total_cost": fte_cost["total_cost"]
                }],
                "total_cost": fte_cost["total_cost"],
                "avg_cost_per_employee": fte_cost["total_cost"] / headcount,
                "description": "Current baseline approach"
            }

        else:
            # All headcount is of the selected employment type
            if employment_type == 'contractor':
                total_cost = self.calculate_contractor_cost(job_role, primary_location, headcount)["total_cost"]
                scenarios["cost_effective"] = {
                    "name": "Most Cost-Effective Mix",
                    "allocation": [{
                        "location": primary_location,
                        "type": "Contractor",
                        "count": headcount,
                        "unit_cost": total_cost / headcount,
                        "total_cost": total_cost
                    }],
                    "total_cost": total_cost,
                    "avg_cost_per_employee": total_cost / headcount,
                    "description": "Optimized for maximum cost savings"
                }
                scenarios["balanced"] = scenarios["cost_effective"]
            else:
                total_cost = self.calculate_fte_cost(job_role, primary_location, headcount)["total_cost"]
                scenarios["cost_effective"] = {
                    "name": "Most Cost-Effective Mix",
                    "allocation": [{
                        "location": primary_location,
                        "type": "FTE",
                        "count": headcount,
                        "unit_cost": total_cost / headcount,
                        "total_cost": total_cost
                    }],
                    "total_cost": total_cost,
                    "avg_cost_per_employee": total_cost / headcount,
                    "description": "Optimized for maximum cost savings"
                }
                scenarios["balanced"] = scenarios["cost_effective"]

            # Current scenario same as cost-effective
            scenarios["current"] = scenarios["cost_effective"]

        return scenarios

# ============================================================================
# PHASE 3: AI EXPLANATION LAYER (Lightweight LLM Simulation)
# ============================================================================
# Replace LightweightLLMService class with:
'''class LightweightLLMService:
    """Real lightweight LLM integration using Phi-3"""
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3-mini-4k-instruct",
            torch_dtype=torch.float32,  # Use float32 for CPU compatibility
            device_map="auto"            # Automatically uses GPU if available
        )
        self.system_prompt = """You are an AI workforce optimization analyst. Provide concise, professional explanations 
        of cost savings based on the following data:"""
    
    def generate_explanation(self, scenarios, job_role):
        current = scenarios["current"]
        cost_effective = scenarios["cost_effective"]
        
        savings = current["total_cost"] - cost_effective["total_cost"]
        savings_pct = (savings / current["total_cost"]) * 100
        
        # Prepare LLM prompt
        prompt = f"""
        {self.system_prompt}
        - Job role: {job_role}
        - Current strategy cost: ${current['total_cost']:,.0f}
        - Optimized strategy cost: ${cost_effective['total_cost']:,.0f}
        - Savings: ${savings:,.0f} ({savings_pct:.1f}%)
        - Optimization strategy: {cost_effective['description']}
        """
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
class LightweightLLMService:
    """Phase 3: Simulates lightweight LLM for generating plain-language explanations"""

    def __init__(self):
        # Simulate lightweight LLM capabilities using template-based generation
        # In production, this would integrate with models like Phi-3 Mini, Qwen2-0.5B, or Gemma 2B
        self.explanation_templates = {
            "cost_savings": [
                "Choosing {location1} over {location2} saves ${savings:,.0f} per employee because:",
                "The cost advantage of {location1} vs {location2} (${savings:,.0f} savings per employee) comes from:",
                "Switching from {location2} to {location1} reduces costs by ${savings:,.0f} per employee due to:"
            ],
            "factors": [
                "{social_charge_diff}% lower social charges",
                "{benefits_diff}% cheaper benefits packages",
                "{salary_diff}% reduced base salary costs",
                "Similar talent availability",
                "Lower regulatory compliance costs",
                "Favorable exchange rates",
                "Reduced infrastructure costs"
            ],
            "contractor_benefits": [
                "Using contractors provides flexibility and {savings_pct}% cost reduction",
                "Contractor model eliminates benefits overhead, saving {savings_pct}%",
                "Contract arrangements reduce long-term commitments while cutting costs by {savings_pct}%"
            ]
        }

    def generate_explanation(self, scenarios: Dict[str, Any], job_role: str) -> str:
        """Generate AI-powered plain-language explanation"""
        cost_effective = scenarios["cost_effective"]
        current = scenarios["current"]

        savings = current["total_cost"] - cost_effective["total_cost"]
        savings_pct = (savings / current["total_cost"]) * 100

        # Simulate LLM reasoning process
        if savings > 0:
            explanation = f"OptiForce AI Analysis: Your optimized workforce strategy saves ${savings:,.0f} ({savings_pct:.1f}%) compared to your current approach."



            # Analyze cost drivers
            primary_location = cost_effective["allocation"][0]["location"]
            current_location = current["allocation"][0]["location"]

            if primary_location != current_location:
                explanation += f"Key insight: Leveraging {primary_location}'s cost advantages provides significant savings through:"

                explanation += "• 65% lower total employment costs"

                explanation += "• Reduced social charges and regulatory overhead"

                explanation += "• Access to high-quality talent at competitive rates"



            # Contractor vs FTE analysis
            contractor_allocation = next((alloc for alloc in cost_effective["allocation"] if alloc["type"] == "Contractor"), None)
            if contractor_allocation:
                explanation += f"Strategic contractor utilization ({contractor_allocation['count']} contractors) eliminates benefits overhead while maintaining operational flexibility."



            explanation += f"Risk mitigation: The recommended mix balances cost optimization with talent quality and operational stability."

        else:
            explanation = "Your current strategy is already well-optimized for cost efficiency. Consider exploring balanced approaches for enhanced operational flexibility."

        return explanation

    def generate_location_comparison(self, location1: str, location2: str, job_role: str) -> str:
        """Generate location-specific comparison insights"""
        # This would use actual LLM in production for dynamic insights
        comparisons = {
            ("india", "usa"): "India offers 75% cost savings vs USA, with strong technical talent pool and English proficiency.",
            ("portugal", "germany"): "Portugal provides 35% cost reduction vs Germany, with similar EU regulatory framework and timezone alignment.",
            ("philippines", "usa"): "Philippines delivers 80% cost savings vs USA, excellent English skills, and cultural compatibility.",
            ("ukraine", "germany"): "Ukraine offers 65% cost reduction vs Germany, with strong technical expertise and European proximity."
        }

        key = (location1.lower(), location2.lower())
        reverse_key = (location2.lower(), location1.lower())

        return comparisons.get(key) or comparisons.get(reverse_key) or f"Geographic arbitrage between {location1} and {location2} provides strategic cost optimization opportunities."
'''
class LightweightLLMService:
    """Real lightweight LLM integration using Phi-3 with Windows support"""
    
    def __init__(self):
        # Disable timeout signals (not supported on Windows)
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        os.environ["HF_HUB_DISABLE_EXPERIMENTAL_WARNING"] = "1"
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-small",
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "google/flan-t5-small",
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
        # Apply 4-bit quantization if possible
        if not torch.cuda.is_available():
            self.model = self.model.to(torch.float32)
        else:
            self.model = self.model.to(torch.float16)
        try:
            self.model = self.model.quantize(4)  # 4-bit quantization
        except:
            pass  # Skip if quantization fails
        self.system_prompt = """You are an AI workforce optimization analyst. Provide concise, professional explanations of cost savings based on the following data:"""
    
    def generate_explanation(self, scenarios, job_role):
        current = scenarios["current"]
        cost_effective = scenarios["cost_effective"]
        
        savings = current["total_cost"] - cost_effective["total_cost"]
        savings_pct = (savings / current["total_cost"]) * 100
        
        # Prepare LLM prompt
        prompt = f"""
        {self.system_prompt}
        - Job role: {job_role}
        - Current strategy cost: ${current['total_cost']:,.0f}
        - Optimized strategy cost: ${cost_effective['total_cost']:,.0f}
        - Savings: ${savings:,.0f} ({savings_pct:.1f}%)
        - Optimization strategy: {cost_effective['description']}
        """
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            attn_implementation='eager'
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# ============================================================================
# PHASE 4: OUTPUT LAYER - FLASK ROUTES
# ============================================================================

# Initialize services
data_service = DataIngestionService()
optimization_engine = OptimizationEngine(data_service)
llm_service = LightweightLLMService()

@app.route('/')
def home():
    """Main application interface"""
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST'])
def optimize_workforce():
    """Main optimization endpoint"""
    try:
        data = request.get_json()

        job_role = data.get('job_role')
        location = data.get('location')
        headcount = int(data.get('headcount', 1))
        constraint = data.get('constraint', 'balanced')

        # Simulate processing time for demonstration
        time.sleep(0.5)

        # Generate scenarios
        scenarios = optimization_engine.generate_scenarios(job_role, location, headcount, constraint)

        # Generate AI explanation
        ai_explanation = llm_service.generate_explanation(scenarios, job_role)

        # Calculate savings
        current_cost = scenarios["current"]["total_cost"]
        optimized_cost = scenarios["cost_effective"]["total_cost"]
        savings = current_cost - optimized_cost
        savings_percentage = (savings / current_cost) * 100 if current_cost > 0 else 0

        response = {
            "scenarios": scenarios,
            "ai_explanation": ai_explanation,
            "savings": {
                "absolute": savings,
                "percentage": savings_percentage,
                "current_cost": current_cost,
                "optimized_cost": optimized_cost
            },
            "metadata": {
                "job_role": job_role,
                "location": location,
                "headcount": headcount,
                "constraint": constraint
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/llm-explain', methods=['POST'])
def llm_explain():
    """Dedicated LLM explanation endpoint"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        # Simulate lightweight LLM processing
        time.sleep(0.3)

        # Generate contextual explanation
        explanation = llm_service.generate_location_comparison(
            data.get('location1', 'India'),
            data.get('location2', 'USA'),
            data.get('job_role', 'Software Engineer')
        )

        return jsonify({"explanation": explanation})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/cost-calculator', methods=['POST'])
def cost_calculator():
    """Real-time cost calculation endpoint"""
    try:
        data = request.get_json()

        job_role = data.get('job_role')
        location = data.get('location')
        employment_type = data.get('employment_type', 'fte')

        if employment_type == 'contractor':
            cost_data = optimization_engine.calculate_contractor_cost(job_role, location)
        else:
            cost_data = optimization_engine.calculate_fte_cost(job_role, location)

        return jsonify(cost_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/locations')
def get_locations():
    """Get available locations data"""
    return jsonify(data_service.locations)

@app.route('/api/job-roles')
def get_job_roles():
    """Get available job roles data"""
    return jsonify(data_service.job_roles)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5050)
