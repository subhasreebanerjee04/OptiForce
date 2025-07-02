// OptiForce MVP - Workforce Cost Optimization Application

// Application Data
const APP_DATA = {
    jobRoles: [
        {"id": "software-engineer", "name": "Software Engineer", "baseMultiplier": 1.0},
        {"id": "data-scientist", "name": "Data Scientist", "baseMultiplier": 1.2},
        {"id": "product-manager", "name": "Product Manager", "baseMultiplier": 1.1},
        {"id": "devops-engineer", "name": "DevOps Engineer", "baseMultiplier": 1.05},
        {"id": "ui-ux-designer", "name": "UI/UX Designer", "baseMultiplier": 0.9},
        {"id": "marketing-manager", "name": "Marketing Manager", "baseMultiplier": 0.95},
        {"id": "sales-manager", "name": "Sales Manager", "baseMultiplier": 1.0},
        {"id": "hr-manager", "name": "HR Manager", "baseMultiplier": 0.85}
    ],
    locations: [
        {"id": "usa", "name": "USA", "costIndex": 1.0, "socialCharges": 0.12, "benefits": 0.25, "contractorPremium": 2.0},
        {"id": "germany", "name": "Germany", "costIndex": 0.85, "socialCharges": 0.45, "benefits": 0.22, "contractorPremium": 1.8},
        {"id": "india", "name": "India", "costIndex": 0.25, "socialCharges": 0.12, "benefits": 0.08, "contractorPremium": 1.2},
        {"id": "portugal", "name": "Portugal", "costIndex": 0.55, "socialCharges": 0.23, "benefits": 0.15, "contractorPremium": 1.5},
        {"id": "poland", "name": "Poland", "costIndex": 0.45, "socialCharges": 0.35, "benefits": 0.18, "contractorPremium": 1.4},
        {"id": "ukraine", "name": "Ukraine", "costIndex": 0.30, "socialCharges": 0.22, "benefits": 0.12, "contractorPremium": 1.3},
        {"id": "philippines", "name": "Philippines", "costIndex": 0.20, "socialCharges": 0.15, "benefits": 0.10, "contractorPremium": 1.2},
        {"id": "mexico", "name": "Mexico", "costIndex": 0.35, "socialCharges": 0.28, "benefits": 0.16, "contractorPremium": 1.4}
    ],
    baseSalaries: {
        "software-engineer": 95000,
        "data-scientist": 110000,
        "product-manager": 105000,
        "devops-engineer": 100000,
        "ui-ux-designer": 85000,
        "marketing-manager": 90000,
        "sales-manager": 95000,
        "hr-manager": 80000
    },
    
    constraints: [
        {"id": "cost-focused", "name": "Cost Focused", "description": "Prioritize maximum cost savings"},
        {"id": "balanced", "name": "Balanced", "description": "Balance cost, risk, and quality"},
        {"id": "quality-focused", "name": "Quality Focused", "description": "Prioritize talent quality and reliability"}
    ]
};

// Global state
let currentAnalysis = null;
let charts = {};
let currentScenario = 'cost-effective';

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

// Cost Calculation Engine
class CostOptimizer {
    constructor() {
        this.scenarios = {};
    }

    calculateEmployeeCost(jobRole, location, headcount, employmentType = 'fte') {
        const baseSalary = APP_DATA.baseSalaries[jobRole];
        const locationData = APP_DATA.locations.find(l => l.id === location);
        const roleData = APP_DATA.jobRoles.find(r => r.id === jobRole);

        if (!baseSalary || !locationData || !roleData) {
            throw new Error('Invalid job role or location');
        }

        // Base salary adjusted for location and role
        const adjustedSalary = baseSalary * locationData.costIndex * roleData.baseMultiplier;
        
        // Social charges and benefits
        const socialCharges = adjustedSalary * locationData.socialCharges;
        const benefits = adjustedSalary * locationData.benefits;
        
        // Total cost per employee
        let costPerEmployee = adjustedSalary + socialCharges + benefits;
        
        // Apply contractor premium if applicable
        if (employmentType === 'contractor') {
            costPerEmployee *= locationData.contractorPremium;
        }

        return {
            baseSalary: adjustedSalary,
            socialCharges,
            benefits,
            totalCost: costPerEmployee,
            totalAnnualCost: costPerEmployee * headcount,
            breakdown: {
                salary: adjustedSalary,
                socialCharges,
                benefits,
                contractorPremium: employmentType === 'contractor' ? costPerEmployee - (adjustedSalary + socialCharges + benefits) : 0
            }
        };
    }

    generateOptimizationScenarios(jobRole, primaryLocation, headcount, constraints) {
        const scenarios = {};
        
        // Current Strategy (all in primary location)
        scenarios.current = {
            name: 'Current Strategy',
            description: 'All employees in primary location',
            distribution: [{ location: primaryLocation, percentage: 1.0, headcount: headcount }],
            totalCost: this.calculateEmployeeCost(jobRole, primaryLocation, headcount).totalAnnualCost,
            risk: 'Low',
            quality: 'High'
        };

        // Most Cost-Effective Mix
        const sortedLocations = APP_DATA.locations
            .map(loc => ({
                ...loc,
                cost: this.calculateEmployeeCost(jobRole, loc.id, 1).totalCost
            }))
            .sort((a, b) => a.cost - b.cost);

        scenarios['cost-effective'] = this.generateCostEffectiveScenario(jobRole, headcount, sortedLocations, constraints);
        scenarios.balanced = this.generateBalancedScenario(jobRole, primaryLocation, headcount, sortedLocations, constraints);

        return scenarios;
    }

    generateCostEffectiveScenario(jobRole, headcount, sortedLocations, constraints) {
        // Distribute across 2-3 most cost-effective locations
        const topLocations = sortedLocations.slice(0, 3);
        let distribution = [];
        let totalCost = 0;

        if (constraints === 'cost-focused') {
            // 70% in cheapest location, 30% distributed among others
            const primary = Math.floor(headcount * 0.7);
            const secondary = Math.floor(headcount * 0.2);
            const tertiary = headcount - primary - secondary;

            distribution = [
                { location: topLocations[0].id, percentage: primary / headcount, headcount: primary },
                { location: topLocations[1].id, percentage: secondary / headcount, headcount: secondary }
            ];

            if (tertiary > 0) {
                distribution.push({ location: topLocations[2].id, percentage: tertiary / headcount, headcount: tertiary });
            }
        } else {
            // More balanced distribution for other constraints
            const each = Math.floor(headcount / 2);
            const remainder = headcount - (each * 2);

            distribution = [
                { location: topLocations[0].id, percentage: each / headcount, headcount: each },
                { location: topLocations[1].id, percentage: (each + remainder) / headcount, headcount: each + remainder }
            ];
        }

        // Calculate total cost
        distribution.forEach(dist => {
            const cost = this.calculateEmployeeCost(jobRole, dist.location, dist.headcount);
            totalCost += cost.totalAnnualCost;
        });

        return {
            name: 'Most Cost-Effective',
            description: 'Optimized for maximum cost savings',
            distribution,
            totalCost,
            risk: 'Medium',
            quality: 'Medium-High'
        };
    }

    generateBalancedScenario(jobRole, primaryLocation, headcount, sortedLocations, constraints) {
        // Mix of primary location and cost-effective alternatives
        const primaryCount = Math.floor(headcount * 0.4);
        const secondaryCount = Math.floor(headcount * 0.4);
        const tertiaryCount = headcount - primaryCount - secondaryCount;

        const distribution = [
            { location: primaryLocation, percentage: primaryCount / headcount, headcount: primaryCount },
            { location: sortedLocations[0].id, percentage: secondaryCount / headcount, headcount: secondaryCount }
        ];

        if (tertiaryCount > 0) {
            distribution.push({ location: sortedLocations[1].id, percentage: tertiaryCount / headcount, headcount: tertiaryCount });
        }

        let totalCost = 0;
        distribution.forEach(dist => {
            const cost = this.calculateEmployeeCost(jobRole, dist.location, dist.headcount);
            totalCost += cost.totalAnnualCost;
        });

        return {
            name: 'Balanced Approach',
            description: 'Balance of cost, risk, and quality',
            distribution,
            totalCost,
            risk: 'Low-Medium',
            quality: 'High'
        };
    }
}

// AI Insights Generator
class AIInsightGenerator {
    generateInsights(scenarios, jobRole, constraints) {
        const insights = [];
        const currentCost = scenarios.current.totalCost;
        const costEffectiveCost = scenarios['cost-effective'].totalCost;
        const savings = currentCost - costEffectiveCost;
        const savingsPercentage = (savings / currentCost) * 100;

        // Cost savings insight
        insights.push({
            title: 'Significant Cost Reduction Opportunity',
            text: `By implementing our most cost-effective strategy, you could save ${formatCurrency(savings)} annually (${savingsPercentage.toFixed(1)}% reduction). This optimization leverages geographic arbitrage while maintaining talent quality through strategic location selection.`
        });

        // Geographic strategy insight
        const costEffectiveDistribution = scenarios['cost-effective'].distribution;
        const primaryLocation = costEffectiveDistribution[0];
        const locationName = APP_DATA.locations.find(l => l.id === primaryLocation.location)?.name;
        
        insights.push({
            title: 'Strategic Geographic Distribution',
            text: `${locationName} emerges as your primary cost-optimization location, offering ${formatPercentage(primaryLocation.percentage)} of your workforce at significantly reduced costs. This location provides an optimal balance of talent availability, cost efficiency, and operational feasibility.`
        });

        // Risk mitigation insight
        insights.push({
            title: 'Risk Mitigation Through Diversification',
            text: `The recommended approach distributes talent across ${costEffectiveDistribution.length} strategic locations, reducing dependency risk while maintaining operational efficiency. This diversification strategy provides resilience against local market fluctuations and regulatory changes.`
        });

        // Implementation timeline insight
        const roleData = APP_DATA.jobRoles.find(r => r.id === jobRole);
        insights.push({
            title: 'Implementation Roadmap',
            text: `For ${roleData?.name} positions, we recommend a phased 6-month implementation timeline. Start with ${Math.floor(costEffectiveDistribution[0].headcount * 0.3)} initial hires to validate the strategy, then scale gradually. Expected payback period: 4-6 months based on current market conditions.`
        });

        return insights;
    }
}

// Chart Manager
class ChartManager {
    constructor() {
        this.charts = {};
    }

    createScenarioChart(scenarios) {
        const ctx = document.getElementById('scenario-chart');
        if (!ctx) return;
        
        if (this.charts.scenario) {
            this.charts.scenario.destroy();
        }

        const data = {
            labels: Object.values(scenarios).map(s => s.name),
            datasets: [{
                label: 'Annual Cost',
                data: Object.values(scenarios).map(s => s.totalCost),
                backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C'],
                borderColor: ['#1FB8CD', '#FFC185', '#B4413C'],
                borderWidth: 2
            }]
        };

        this.charts.scenario = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    createLocationChart(scenarios) {
        const ctx = document.getElementById('location-chart');
        if (!ctx) return;
        
        if (this.charts.location) {
            this.charts.location.destroy();
        }

        const locationCosts = APP_DATA.locations.map(location => {
            const cost = new CostOptimizer().calculateEmployeeCost('software-engineer', location.id, 1).totalCost;
            return {
                location: location.name,
                cost: cost
            };
        }).sort((a, b) => a.cost - b.cost);

        const data = {
            labels: locationCosts.map(l => l.location),
            datasets: [{
                label: 'Cost per Employee',
                data: locationCosts.map(l => l.cost),
                backgroundColor: '#1FB8CD',
                borderColor: '#1FB8CD',
                borderWidth: 1
            }]
        };

        this.charts.location = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    createBreakdownChart(jobRole, location) {
        const ctx = document.getElementById('breakdown-chart');
        if (!ctx) return;
        
        if (this.charts.breakdown) {
            this.charts.breakdown.destroy();
        }

        const cost = new CostOptimizer().calculateEmployeeCost(jobRole, location, 1);
        
        const data = {
            labels: ['Base Salary', 'Social Charges', 'Benefits'],
            datasets: [{
                data: [
                    cost.breakdown.salary,
                    cost.breakdown.socialCharges,
                    cost.breakdown.benefits
                ],
                backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C'],
                borderWidth: 0
            }]
        };

        this.charts.breakdown = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Application Controller
class OptiForceApp {
    constructor() {
        this.costOptimizer = new CostOptimizer();
        this.insightGenerator = new AIInsightGenerator();
        this.chartManager = new ChartManager();
        this.init();
    }

    init() {
        this.bindEvents();
        this.showPage('landing-page');
    }

    bindEvents() {
        // Form submission
        const form = document.getElementById('workforce-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.processForm();
            });
        }

        // Back to form button
        const backBtn = document.getElementById('back-to-form');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.showPage('landing-page');
            });
        }

        // Scenario tabs
        document.querySelectorAll('.scenario-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchScenario(e.target.dataset.scenario);
            });
        });
    }

    showPage(pageId) {
        document.querySelectorAll('.page-section').forEach(page => {
            page.classList.remove('active');
        });
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        }
    }

    processForm() {
        // Get form data
        const formData = {
            jobRole: document.getElementById('job-role').value,
            location: document.getElementById('location').value,
            headcount: parseInt(document.getElementById('headcount').value),
            constraints: document.getElementById('constraints').value,
            employment_type: document.getElementById('employment-type').value
        };

        // Validate form
        if (!formData.jobRole || !formData.location || !formData.headcount || !formData.constraints || !formData.employment_type) {
            alert('Please fill in all required fields.');
            return;
        }

        this.showLoadingScreen(formData);
    }

    showLoadingScreen(formData) {
        this.showPage('loading-screen');
        
        // Reset loading state
        document.querySelectorAll('.phase-item').forEach(item => {
            item.classList.remove('active', 'completed');
        });
        document.getElementById('progress-fill').style.width = '0%';
        
        // Simulate processing phases
        const phases = ['phase-1', 'phase-2', 'phase-3', 'phase-4'];
        let currentPhase = 0;
        
        const processPhase = () => {
            if (currentPhase > 0) {
                const prevPhase = document.getElementById(phases[currentPhase - 1]);
                if (prevPhase) {
                    prevPhase.classList.remove('active');
                    prevPhase.classList.add('completed');
                }
            }
            
            if (currentPhase < phases.length) {
                const currentPhaseElement = document.getElementById(phases[currentPhase]);
                if (currentPhaseElement) {
                    currentPhaseElement.classList.add('active');
                }
                
                const progressFill = document.getElementById('progress-fill');
                if (progressFill) {
                    progressFill.style.width = `${((currentPhase + 1) / phases.length) * 100}%`;
                }
                
                currentPhase++;
                setTimeout(processPhase, 800);
            } else {
                // Processing complete, show dashboard
                setTimeout(() => {
                    this.showDashboard(formData);
                }, 500);
            }
        };
        
        processPhase();
    }

    showDashboard(formData) {
        try {
            // Generate analysis
            currentAnalysis = {
                formData,
                scenarios: this.costOptimizer.generateOptimizationScenarios(
                    formData.jobRole,
                    formData.location,
                    formData.headcount,
                    formData.constraints
                )
            };

            // Show dashboard first
            this.showPage('dashboard');
            
            // Then update content
            setTimeout(() => {
                this.updateMetrics();
                this.updateInsights();
                this.createCharts();
                this.setupCalculator();
                this.updateScenarioDetails('cost-effective');
            }, 100);
            
        } catch (error) {
            console.error('Error showing dashboard:', error);
            alert('Error generating analysis. Please try again.');
            this.showPage('landing-page');
        }
    }

    updateMetrics() {
        if (!currentAnalysis) return;
        
        const { scenarios } = currentAnalysis;
        const currentCost = scenarios.current.totalCost;
        const costEffectiveCost = scenarios['cost-effective'].totalCost;
        const savings = currentCost - costEffectiveCost;
        const savingsPercentage = (savings / currentCost) * 100;

        const elements = {
            'potential-savings': formatCurrency(savings),
            'optimal-locations': scenarios['cost-effective'].distribution.length,
            'cost-reduction': `${savingsPercentage.toFixed(1)}%`,
            'payback-period': '4-6 months'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    updateInsights() {
        if (!currentAnalysis) return;
        
        const { scenarios, formData } = currentAnalysis;
        const insights = this.insightGenerator.generateInsights(scenarios, formData.jobRole, formData.constraints);
        
        const container = document.getElementById('ai-insights');
        if (container) {
            container.innerHTML = insights.map(insight => `
                <div class="insight-item">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-text">${insight.text}</div>
                </div>
            `).join('');
        }
    }

    createCharts() {
        if (!currentAnalysis) return;
        
        const { scenarios, formData } = currentAnalysis;
        
        try {
            this.chartManager.createScenarioChart(scenarios);
            this.chartManager.createLocationChart(scenarios);
            this.chartManager.createBreakdownChart(formData.jobRole, formData.location);
        } catch (error) {
            console.error('Error creating charts:', error);
        }
    }

    setupCalculator() {
        if (!currentAnalysis) return;
        
        const { scenarios, formData } = currentAnalysis;
        const container = document.getElementById('location-sliders');
        if (!container) return;
        
        // Create sliders for location distribution
        const distribution = scenarios['cost-effective'].distribution;
        
        container.innerHTML = distribution.map((dist, index) => {
            const locationName = APP_DATA.locations.find(l => l.id === dist.location)?.name;
            const percentage = Math.round(dist.percentage * 100);
            
            return `
                <div class="slider-item">
                    <div class="slider-label">${locationName}</div>
                    <input type="range" class="slider" min="0" max="100" value="${percentage}" 
                           data-location="${dist.location}" id="slider-${index}">
                    <div class="slider-value">${percentage}%</div>
                </div>
            `;
        }).join('');

        // Bind slider events
        container.querySelectorAll('.slider').forEach(slider => {
            slider.addEventListener('input', () => {
                this.updateCalculatorResults();
            });
        });

        this.updateCalculatorResults();
    }

    updateCalculatorResults() {
        if (!currentAnalysis) return;
        
        const { formData } = currentAnalysis;
        const sliders = document.querySelectorAll('#location-sliders .slider');
        let totalCost = 0;

        // Calculate costs based on current slider values
        sliders.forEach(slider => {
            const location = slider.dataset.location;
            const percentage = parseInt(slider.value) / 100;
            const headcount = Math.round(formData.headcount * percentage);
            
            if (headcount > 0) {
                try {
                    const cost = this.costOptimizer.calculateEmployeeCost(formData.jobRole, location, headcount);
                    totalCost += cost.totalAnnualCost;
                } catch (error) {
                    console.error('Error calculating cost:', error);
                }
            }
            
            // Update slider value display
            const valueDisplay = slider.parentNode.querySelector('.slider-value');
            if (valueDisplay) {
                valueDisplay.textContent = `${slider.value}%`;
            }
        });

        // Calculate savings
        const currentCost = currentAnalysis.scenarios.current.totalCost;
        const savings = currentCost - totalCost;
        const roi = totalCost > 0 ? (savings / currentCost) * 100 : 0;

        // Update display
        const elements = {
            'calc-total-cost': formatCurrency(totalCost),
            'calc-savings': formatCurrency(savings),
            'calc-roi': `${roi.toFixed(1)}%`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    switchScenario(scenario) {
        currentScenario = scenario;
        
        // Update tab states
        document.querySelectorAll('.scenario-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        const activeTab = document.querySelector(`[data-scenario="${scenario}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Update scenario details
        this.updateScenarioDetails(scenario);
    }

    updateScenarioDetails(scenario) {
        if (!currentAnalysis) return;
        
        const scenarioData = currentAnalysis.scenarios[scenario];
        const container = document.getElementById('scenario-details');
        if (!container || !scenarioData) return;
        
        const statusClass = scenario === 'cost-effective' ? 'success' : 
                           scenario === 'balanced' ? 'warning' : 'info';
        
        container.innerHTML = `
            <div class="scenario-status">
                <span class="status status--${statusClass}">${scenarioData.name}</span>
            </div>
            <h4>Total Annual Cost</h4>
            <div class="metric-value">${formatCurrency(scenarioData.totalCost)}</div>
            
            <h4>Risk Level</h4>
            <p>${scenarioData.risk}</p>
            
            <h4>Quality Level</h4>
            <p>${scenarioData.quality}</p>
            
            <h4>Location Distribution</h4>
            <div class="location-distribution">
                ${scenarioData.distribution.map(dist => {
                    const locationName = APP_DATA.locations.find(l => l.id === dist.location)?.name;
                    return `
                        <div class="location-item">
                            <span class="location-name">${locationName}</span>
                            <span class="location-percentage">${Math.round(dist.percentage * 100)}%</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OptiForceApp();
});
