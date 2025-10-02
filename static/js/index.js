
// Job Application Management System JavaScript
class JobManagementSystem {
    constructor() {
        this.init();
        this.bindEvents();
    }

    init() {
        this.jobs = [
            {
                id: 1,
                title: "Senior Frontend Developer",
                company: "TechCorp Inc.",
                location: "San Francisco, CA",
                salary: "$90k - $120k",
                type: "Full-time",
                remote: "Remote friendly",
                skills: ["React", "TypeScript", "Node.js"],
                matchScore: 92,
                posted: "2 days ago",
                description: "Join our innovative team building next-gen web applications..."
            },
            {
                id: 2,
                title: "Full Stack Developer",
                company: "DataSoft Solutions",
                location: "New York, NY",
                salary: "$85k - $110k",
                type: "Full-time",
                remote: "Hybrid",
                skills: ["React", "Python", "AWS"],
                matchScore: 78,
                posted: "5 days ago",
                description: "Looking for a versatile developer to work on our data platform..."
            }
        ];

        this.applications = [
            {
                id: 1,
                jobTitle: "Senior Frontend Developer",
                company: "TechCorp Inc.",
                status: "interview",
                appliedDate: "2024-10-15",
                progress: 60,
                nextStep: "Technical interview on Oct 25"
            },
            {
                id: 2,
                jobTitle: "Full Stack Developer",
                company: "DataSoft Solutions",
                status: "applied",
                appliedDate: "2024-10-10",
                progress: 30,
                nextStep: "Waiting for response"
            }
        ];
    }

    bindEvents() {
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const parent = e.target.closest('div');
                parent.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.filterJobs();
            });
        });

        // Apply buttons
        document.querySelectorAll('.btn:contains("Apply Now")').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.showApplicationForm(e.target.closest('.card'));
            });
        });

        // Save job buttons
        document.querySelectorAll('.btn:contains("Save")').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.saveJob(e.target.closest('.card'));
            });
        });

        // AI recommendation buttons
        document.querySelectorAll('.btn-ai').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.target.textContent.includes('Refresh')) {
                    this.refreshAIRecommendations();
                } else if (e.target.textContent.includes('Interview Prep')) {
                    this.showInterviewPrep();
                } else {
                    this.showAIAssistant();
                }
            });
        });

        // Application status updates
        this.initializeStatusUpdates();
    }

    filterJobs() {
        const activeFilters = {
            jobType: document.querySelector('.filter-chip.active').textContent.trim(),
            experience: document.querySelectorAll('.filter-chip.active')[1]?.textContent.trim(),
            salary: document.querySelector('select').value
        };

        // Simulate filtering logic
        console.log('Filtering jobs with:', activeFilters);
        this.showFilteredResults(activeFilters);
    }

    showFilteredResults(filters) {
        // Add loading animation
        const jobsList = document.getElementById('jobsList');
        jobsList.style.opacity = '0.5';
        
        setTimeout(() => {
            jobsList.style.opacity = '1';
            this.showNotification('Jobs filtered based on your preferences', 'success');
        }, 500);
    }

    refreshAIRecommendations() {
        const btn = event.target;
        const originalText = btn.innerHTML;
        
        // Show loading state
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            this.showNotification('AI recommendations updated based on latest market data', 'success');
            this.updateMatchScores();
        }, 2000);
    }

    updateMatchScores() {
        // Simulate AI recalculation of match scores
        document.querySelectorAll('.match-score').forEach((score, index) => {
            const newScore = Math.max(70, Math.min(95, Math.floor(Math.random() * 25) + 70));
            const icon = score.querySelector('i');
            const text = `${newScore}% Match`;
            
            score.innerHTML = `${icon.outerHTML} ${text}`;
            
            // Update color based on new score
            score.className = 'match-score';
            if (newScore >= 85) score.classList.add('match-high');
            else if (newScore >= 70) score.classList.add('match-medium');
            else score.classList.add('match-low');
        });
    }

    showApplicationForm(jobCard) {
        const jobTitle = jobCard.querySelector('h6').textContent;
        const company = jobCard.querySelector('.text-muted').textContent.split(' • ')[0];
        
        // Create and show application modal
        const modalHtml = `
            <div class="modal fade" id="applyModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Apply for ${jobTitle}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>Company:</strong> ${company}</p>
                            <div class="ai-recommendation mb-3">
                                <h6 class="fw-bold mb-2 mt-2">AI Application Tips</h6>
                                <ul class="small mb-0">
                                    <li>Highlight your React experience prominently</li>
                                    <li>Mention specific projects with TypeScript</li>
                                    <li>Include metrics about performance improvements</li>
                                </ul>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Cover Letter</label>
                                <textarea class="form-control" rows="4" placeholder="AI will help optimize your cover letter..."></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Resume</label>
                                <select class="form-select">
                                    <option>Resume_JohnDoe_2024.pdf (Recommended by AI)</option>
                                    <option>Resume_JohnDoe_Generic.pdf</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-ai" onclick="jobSystem.submitApplication()">
                                <i class="fas fa-paper-plane me-1"></i>Submit Application
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('applyModal');
        if (existingModal) existingModal.remove();
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('applyModal'));
        modal.show();
    }

    submitApplication() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('applyModal'));
        modal.hide();
        
        // Simulate application submission
        setTimeout(() => {
            this.showNotification('Application submitted successfully! AI is tracking your progress.', 'success');
            this.updateApplicationStats();
        }, 500);
    }

    saveJob(jobCard) {
        const btn = jobCard.querySelector('.btn:contains("Save")');
        const icon = btn.querySelector('i');
        
        if (icon.classList.contains('fa-heart')) {
            icon.classList.remove('fa-heart');
            icon.classList.add('fa-heart', 'text-danger');
            btn.classList.add('text-danger');
            this.showNotification('Job saved to your favorites', 'success');
        } else {
            icon.classList.remove('text-danger');
            btn.classList.remove('text-danger');
            this.showNotification('Job removed from favorites', 'info');
        }
    }

    showAIAssistant() {
        const modal = new bootstrap.Modal(document.getElementById('aiAssistantModal'));
        modal.show();
    }

    showInterviewPrep() {
        this.showNotification('AI Interview Preparation module launching...', 'info');
        
        // Simulate opening interview prep
        setTimeout(() => {
            const prepModal = `
                <div class="modal fade" id="interviewPrepModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-brain me-2"></i>AI Interview Preparation
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="ai-recommendation mb-4">
                                    <h6 class="fw-bold mb-2 mt-2">Personalized Interview Strategy</h6>
                                    <p class="mb-2">Based on the job requirements and your profile:</p>
                                </div>
                                
                                <div class="row mb-4">
                                    <div class="col-md-4">
                                        <div class="text-center p-3 bg-light rounded">
                                            <i class="fas fa-code text-primary fa-2x mb-2"></i>
                                            <h6>Technical Questions</h6>
                                            <button class="btn btn-sm btn-primary">Practice Now</button>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="text-center p-3 bg-light rounded">
                                            <i class="fas fa-users text-success fa-2x mb-2"></i>
                                            <h6>Behavioral Questions</h6>
                                            <button class="btn btn-sm btn-success">Practice Now</button>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="text-center p-3 bg-light rounded">
                                            <i class="fas fa-sitemap text-info fa-2x mb-2"></i>
                                            <h6>System Design</h6>
                                            <button class="btn btn-sm btn-info">Practice Now</button>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <h6>Mock Interview Simulator</h6>
                                    <p class="text-muted">Practice with our AI interviewer that adapts to the specific role</p>
                                    <button class="btn btn-ai">
                                        <i class="fas fa-play me-1"></i>Start Mock Interview
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', prepModal);
            const modal = new bootstrap.Modal(document.getElementById('interviewPrepModal'));
            modal.show();
        }, 1000);
    }

    initializeStatusUpdates() {
        // Simulate real-time status updates
        setInterval(() => {
            this.checkForUpdates();
        }, 30000); // Check every 30 seconds
    }

    checkForUpdates() {
        // Simulate receiving updates from companies
        if (Math.random() > 0.95) { // 5% chance of update
            const updates = [
                "TechCorp has reviewed your application",
                "New interview scheduled for next week",
                "DataSoft wants to schedule a call",
                "AI found 3 new matching positions"
            ];
            
            const randomUpdate = updates[Math.floor(Math.random() * updates.length)];
            this.showNotification(randomUpdate, 'info');
        }
    }

    updateApplicationStats() {
        // Update dashboard statistics
        const statsCards = document.querySelectorAll('.card-title');
        if (statsCards.length > 0) {
            const currentApps = parseInt(statsCards[0].textContent);
            statsCards[0].textContent = currentApps + 1;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // AI-powered job matching algorithm simulation
    calculateJobMatch(userProfile, jobRequirements) {
        const skillMatch = this.calculateSkillMatch(userProfile.skills, jobRequirements.skills);
        const experienceMatch = this.calculateExperienceMatch(userProfile.experience, jobRequirements.experience);
        const locationMatch = this.calculateLocationMatch(userProfile.location, jobRequirements.location);
        const salaryMatch = this.calculateSalaryMatch(userProfile.expectedSalary, jobRequirements.salary);

        // Weighted average
        const weights = {
            skills: 0.4,
            experience: 0.3,
            location: 0.2,
            salary: 0.1
        };

        return Math.round(
            skillMatch * weights.skills +
            experienceMatch * weights.experience +
            locationMatch * weights.location +
            salaryMatch * weights.salary
        );
    }

    calculateSkillMatch(userSkills, requiredSkills) {
        const matchingSkills = userSkills.filter(skill => 
            requiredSkills.some(req => req.toLowerCase().includes(skill.toLowerCase()))
        );
        return Math.min(100, (matchingSkills.length / requiredSkills.length) * 100);
    }

    calculateExperienceMatch(userExp, requiredExp) {
        const expDiff = Math.abs(userExp - requiredExp);
        return Math.max(0, 100 - (expDiff * 10));
    }

    calculateLocationMatch(userLocation, jobLocation) {
        if (jobLocation.includes('Remote')) return 100;
        if (userLocation.city === jobLocation.city) return 100;
        if (userLocation.state === jobLocation.state) return 80;
        return 60;
    }

    calculateSalaryMatch(expectedSalary, offeredSalary) {
        const salaryDiff = Math.abs(expectedSalary - offeredSalary) / expectedSalary;
        return Math.max(0, 100 - (salaryDiff * 100));
    }

    // Advanced search and filtering
    performAdvancedSearch(query, filters) {
        return this.jobs.filter(job => {
            const titleMatch = job.title.toLowerCase().includes(query.toLowerCase());
            const companyMatch = job.company.toLowerCase().includes(query.toLowerCase());
            const skillsMatch = job.skills.some(skill => 
                skill.toLowerCase().includes(query.toLowerCase())
            );

            const queryMatch = titleMatch || companyMatch || skillsMatch;

            // Apply filters
            const typeMatch = !filters.jobType || job.type === filters.jobType;
            const locationMatch = !filters.location || job.location.includes(filters.location);
            const remoteMatch = !filters.remote || job.remote === filters.remote;

            return queryMatch && typeMatch && locationMatch && remoteMatch;
        });
    }

    // Analytics and insights
    generateCareerInsights() {
        const insights = {
            applicationTrends: this.analyzeApplicationTrends(),
            skillGaps: this.identifySkillGaps(),
            marketDemand: this.analyzeMarketDemand(),
            salaryBenchmark: this.calculateSalaryBenchmark(),
            competitionLevel: this.assessCompetitionLevel()
        };

        return insights;
    }

    analyzeApplicationTrends() {
        // Simulate application trend analysis
        return {
            totalApplications: 24,
            responseRate: 32,
            averageResponseTime: 5.2,
            topCompanyTypes: ['Tech Startups', 'Fortune 500', 'Mid-size Companies'],
            weeklyTrend: [3, 5, 2, 4, 6, 3, 1] // Last 7 days
        };
    }

    identifySkillGaps() {
        return [
            { skill: 'Next.js', demand: 'High', currentLevel: 'Beginner' },
            { skill: 'GraphQL', demand: 'Medium', currentLevel: 'None' },
            { skill: 'Docker', demand: 'High', currentLevel: 'Intermediate' }
        ];
    }

    analyzeMarketDemand() {
        return {
            hotSkills: ['React', 'TypeScript', 'Python', 'AWS'],
            growingIndustries: ['Fintech', 'Healthcare Tech', 'E-commerce'],
            averageSalaryIncrease: '12%',
            jobOpeningsGrowth: '18%'
        };
    }

    calculateSalaryBenchmark() {
        return {
            yourRange: '$90k - $120k',
            marketAverage: '$105k',
            percentile: '75th',
            locationAdjustment: '+15%'
        };
    }

    assessCompetitionLevel() {
        return {
            level: 'Moderate',
            averageApplicationsPerJob: 45,
            yourCompetitiveAdvantage: ['Strong React skills', 'Good portfolio', 'Relevant experience'],
            improvementAreas: ['Add certifications', 'Expand backend skills']
        };
    }
}

// Initialize the job management system
const jobSystem = new JobManagementSystem();

// Additional event listeners for enhanced functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Add dynamic search functionality
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length > 2) {
                    jobSystem.performAdvancedSearch(query, {});
                }
            }, 300);
        });
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                bootstrap.Modal.getInstance(openModal)?.hide();
            }
        }
    });

    // Add progress bars animation
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 500);
    });

    // Add timeline styling
    const timelineCSS = `
        <style>
        .timeline {
            position: relative;
            padding-left: 2rem;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 0.75rem;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e5e7eb;
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .timeline-marker {
            position: absolute;
            left: -2.25rem;
            top: 0.25rem;
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 0 3px currentColor;
        }
        
        .timeline-content h6 {
            margin-bottom: 0.25rem;
            font-weight: 600;
        }
        
        .timeline-item.completed .timeline-marker {
            background: #10b981;
        }
        
        .timeline-item.active .timeline-marker {
            background: #f59e0b;
        }
        
        .timeline-item:not(.completed):not(.active) .timeline-marker {
            background: #e5e7eb;
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', timelineCSS);

    // Initialize real-time updates
    setInterval(() => {
        // Simulate live job updates
        const badges = document.querySelectorAll('.badge');
        badges.forEach(badge => {
            if (badge.textContent === 'New' && Math.random() > 0.8) {
                badge.textContent = 'Hot';
                badge.className = 'badge bg-danger';
            }
        });
    }, 10000);

    // Add loading states for async operations
    window.showLoading = function(element, text = 'Loading...') {
        element.disabled = true;
        element.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
    };

    window.hideLoading = function(element, originalText) {
        element.disabled = false;
        element.innerHTML = originalText;
    };
});

// Advanced AI recommendation engine simulation
class AIRecommendationEngine {
    constructor() {
        this.userProfile = {
            skills: ['React', 'JavaScript', 'TypeScript', 'CSS', 'Node.js'],
            experience: 4,
            location: { city: 'San Francisco', state: 'CA' },
            expectedSalary: 100000,
            preferences: {
                remote: true,
                companySize: 'medium',
                industry: 'tech'
            }
        };
    }

    generatePersonalizedRecommendations() {
        return {
            jobRecommendations: this.getJobRecommendations(),
            skillRecommendations: this.getSkillRecommendations(),
            careerPathSuggestions: this.getCareerPathSuggestions(),
            networkingOpportunities: this.getNetworkingOpportunities(),
            salaryOptimization: this.getSalaryOptimization()
        };
    }

    getJobRecommendations() {
        return [
            {
                title: 'Senior React Developer',
                company: 'InnovateX',
                matchScore: 94,
                reasons: ['Perfect skill match', 'Salary aligns', 'Remote-friendly'],
                urgency: 'high'
            },
            {
                title: 'Frontend Tech Lead',
                company: 'TechForward',
                matchScore: 89,
                reasons: ['Leadership opportunity', 'Technology stack match'],
                urgency: 'medium'
            }
        ];
    }

    getSkillRecommendations() {
        return [
            {
                skill: 'Next.js',
                priority: 'high',
                impact: '+23% job matches',
                timeToLearn: '2-3 weeks',
                resources: ['Official documentation', 'Online courses']
            },
            {
                skill: 'GraphQL',
                priority: 'medium',
                impact: '+15% salary potential',
                timeToLearn: '3-4 weeks',
                resources: ['GraphQL tutorials', 'Practice projects']
            }
        ];
    }

    getCareerPathSuggestions() {
        return [
            {
                path: 'Frontend Architect',
                timeline: '2-3 years',
                requiredSkills: ['System design', 'Team leadership', 'Advanced React patterns'],
                salaryRange: '$130k - $160k'
            },
            {
                path: 'Full-Stack Tech Lead',
                timeline: '1-2 years',
                requiredSkills: ['Backend development', 'DevOps basics', 'Team management'],
                salaryRange: '$120k - $150k'
            }
        ];
    }

    getNetworkingOpportunities() {
        return [
            {
                event: 'React Conference 2024',
                date: '2024-11-15',
                type: 'Conference',
                relevance: 'Perfect for React developers',
                expectedContacts: '50+ professionals'
            },
            {
                event: 'Bay Area Frontend Meetup',
                date: '2024-11-02',
                type: 'Meetup',
                relevance: 'Local networking opportunity',
                expectedContacts: '20+ professionals'
            }
        ];
    }

    getSalaryOptimization() {
        return {
            currentEstimate: '$95k - $120k',
            optimizedRange: '$105k - $135k',
            improvements: [
                'Add Next.js certification',
                'Highlight leadership experience',
                'Negotiate based on market data'
            ],
            marketComparison: '15% above average'
        };
    }
}

// Initialize AI recommendation engine
const aiEngine = new AIRecommendationEngine();

// Export for use in other scripts
window.jobManagementSystem = jobSystem;
window.aiRecommendationEngine = aiEngine;
