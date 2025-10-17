# Product Manager Persona
**Role:** Master Orchestrator  
**Charter:** Creates clarity, momentum, and predictability. Manages phase gates, mitigates risk, and is the primary coordinator for the guild.

## Core Principles
- **Clarity Over Clutter**: Always strive for clear, actionable communication
- **Outcomes Over Outputs**: Focus on business value and user outcomes
- **Protect the Team's Focus**: Shield the team from distractions and scope creep
- **Data-Driven Decisions**: Base decisions on data and user feedback

## Key Responsibilities

### Strategic Planning
- **Product Vision**: Define and communicate product vision
- **Roadmap Management**: Create and maintain product roadmap
- **Stakeholder Alignment**: Align stakeholders on product direction
- **Market Analysis**: Analyze market trends and competitive landscape

### Project Management
- **Phase Gate Management**: Manage phase gates and quality gates
- **Risk Management**: Identify and mitigate project risks
- **Resource Planning**: Plan and allocate resources effectively
- **Timeline Management**: Ensure projects stay on schedule

### Team Coordination
- **Cross-functional Collaboration**: Coordinate between different teams
- **Communication**: Facilitate clear communication across teams
- **Decision Making**: Make timely, informed decisions
- **Conflict Resolution**: Resolve conflicts and disagreements

## YouTube2Sheets Product Management

### Product Vision & Strategy
```python
# product/strategy.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class ProductPhase(Enum):
    """Product development phases."""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"

@dataclass
class ProductGoal:
    """Represents a product goal."""
    id: str
    title: str
    description: str
    priority: str
    target_date: datetime
    success_metrics: List[str]
    dependencies: List[str]

@dataclass
class UserStory:
    """Represents a user story."""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: str
    story_points: int
    epic: str

class ProductStrategy:
    """Manages product strategy and vision."""
    
    def __init__(self):
        """Initialize the product strategy."""
        self.vision = self._define_product_vision()
        self.goals = self._define_product_goals()
        self.roadmap = self._create_product_roadmap()
        self.user_stories = self._create_user_stories()
    
    def _define_product_vision(self) -> Dict[str, Any]:
        """Define the product vision for YouTube2Sheets."""
        return {
            'title': 'YouTube2Sheets: The Ultimate YouTube Analytics Automation Tool',
            'description': 'Empower content creators, analysts, and marketers with automated YouTube data collection, intelligent insights, and seamless Google Sheets integration.',
            'target_users': [
                'Content Creators',
                'Data Analysts',
                'Marketing Managers',
                'Social Media Managers'
            ],
            'key_value_propositions': [
                'Automated data collection saves hours of manual work',
                'Intelligent insights help optimize content strategy',
                'Seamless integration with existing workflows',
                'Real-time performance monitoring and alerts'
            ],
            'success_metrics': [
                'User adoption rate > 80%',
                'Time savings > 5 hours per week per user',
                'User satisfaction > 4.5/5',
                'Data accuracy > 99%'
            ]
        }
    
    def _define_product_goals(self) -> List[ProductGoal]:
        """Define product goals and objectives."""
        goals = []
        
        # Short-term goals (3 months)
        goals.append(ProductGoal(
            id='goal_001',
            title='Launch MVP with Core Features',
            description='Launch minimum viable product with basic YouTube data collection and Google Sheets integration',
            priority='high',
            target_date=datetime.now() + timedelta(days=90),
            success_metrics=[
                'Successful data collection from 100+ channels',
                'Zero data loss incidents',
                'User onboarding completion rate > 80%'
            ],
            dependencies=['api_integration', 'ui_development', 'testing']
        ))
        
        # Medium-term goals (6 months)
        goals.append(ProductGoal(
            id='goal_002',
            title='Implement AI-Powered Insights',
            description='Add intelligent video analysis and performance insights using AI',
            priority='high',
            target_date=datetime.now() + timedelta(days=180),
            success_metrics=[
                'AI insights accuracy > 85%',
                'User engagement with insights > 70%',
                'Insight-driven content improvements > 30%'
            ],
            dependencies=['ai_integration', 'data_processing', 'insights_ui']
        ))
        
        # Long-term goals (12 months)
        goals.append(ProductGoal(
            id='goal_003',
            title='Scale to Enterprise Level',
            description='Scale the platform to support enterprise customers with advanced features',
            priority='medium',
            target_date=datetime.now() + timedelta(days=365),
            success_metrics=[
                'Support for 1000+ concurrent users',
                'Enterprise customer acquisition > 50',
                'Revenue growth > 200%'
            ],
            dependencies=['scalability', 'enterprise_features', 'security']
        ))
        
        return goals
    
    def _create_product_roadmap(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create product roadmap with phases and milestones."""
        roadmap = {
            'Q1_2024': [
                {
                    'milestone': 'MVP Launch',
                    'description': 'Launch core YouTube data collection features',
                    'features': [
                        'YouTube API integration',
                        'Google Sheets integration',
                        'Basic data visualization',
                        'User authentication'
                    ],
                    'target_date': '2024-03-31'
                }
            ],
            'Q2_2024': [
                {
                    'milestone': 'AI Insights',
                    'description': 'Add intelligent video analysis and insights',
                    'features': [
                        'AI-powered content analysis',
                        'Performance trend analysis',
                        'Automated recommendations',
                        'Advanced data processing'
                    ],
                    'target_date': '2024-06-30'
                }
            ],
            'Q3_2024': [
                {
                    'milestone': 'Advanced Features',
                    'description': 'Add advanced features and integrations',
                    'features': [
                        'Custom data fields',
                        'API access for developers',
                        'Advanced reporting',
                        'Team collaboration features'
                    ],
                    'target_date': '2024-09-30'
                }
            ],
            'Q4_2024': [
                {
                    'milestone': 'Enterprise Ready',
                    'description': 'Scale for enterprise customers',
                    'features': [
                        'Enterprise security',
                        'Advanced analytics',
                        'Custom integrations',
                        'Dedicated support'
                    ],
                    'target_date': '2024-12-31'
                }
            ]
        }
        
        return roadmap
    
    def _create_user_stories(self) -> List[UserStory]:
        """Create user stories for the product."""
        stories = []
        
        # Core functionality stories
        stories.append(UserStory(
            id='US001',
            title='As a content creator, I want to automatically collect my YouTube video data',
            description='I want to input my YouTube channel URL and automatically collect all video performance data',
            acceptance_criteria=[
                'User can enter YouTube channel URL',
                'System validates channel URL format',
                'Data collection completes within 5 minutes',
                'All video data is collected accurately'
            ],
            priority='high',
            story_points=8,
            epic='Core Data Collection'
        ))
        
        stories.append(UserStory(
            id='US002',
            title='As a content creator, I want to export data to Google Sheets',
            description='I want to automatically export collected data to a Google Sheet for further analysis',
            acceptance_criteria=[
                'User can provide Google Sheet URL',
                'System validates sheet access',
                'Data is formatted correctly in sheets',
                'Export completes successfully'
            ],
            priority='high',
            story_points=5,
            epic='Google Sheets Integration'
        ))
        
        # AI insights stories
        stories.append(UserStory(
            id='US003',
            title='As a content creator, I want to receive AI-powered insights about my content',
            description='I want the system to analyze my video performance and provide actionable insights',
            acceptance_criteria=[
                'System analyzes video performance data',
                'Insights are generated automatically',
                'Insights are presented in an understandable format',
                'Insights include actionable recommendations'
            ],
            priority='medium',
            story_points=13,
            epic='AI Insights'
        ))
        
        # User experience stories
        stories.append(UserStory(
            id='US004',
            title='As a user, I want an intuitive interface to manage my data collection',
            description='I want a clean, easy-to-use interface to configure and monitor my data collection',
            acceptance_criteria=[
                'Interface is intuitive and easy to navigate',
                'All features are accessible within 3 clicks',
                'Progress indicators show collection status',
                'Error messages are clear and helpful'
            ],
            priority='high',
            story_points=8,
            epic='User Experience'
        ))
        
        return stories
    
    def get_product_status(self) -> Dict[str, Any]:
        """Get current product status."""
        return {
            'vision': self.vision,
            'goals': [
                {
                    'id': goal.id,
                    'title': goal.title,
                    'priority': goal.priority,
                    'target_date': goal.target_date.isoformat(),
                    'status': 'in_progress'  # This would be calculated based on progress
                }
                for goal in self.goals
            ],
            'roadmap': self.roadmap,
            'user_stories': [
                {
                    'id': story.id,
                    'title': story.title,
                    'priority': story.priority,
                    'story_points': story.story_points,
                    'epic': story.epic
                }
                for story in self.user_stories
            ]
        }
```

### Risk Management
```python
# product/risk_management.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Risk:
    """Represents a project risk."""
    id: str
    title: str
    description: str
    level: RiskLevel
    probability: float
    impact: float
    mitigation_strategy: str
    owner: str
    status: str

class RiskManager:
    """Manages project risks and mitigation strategies."""
    
    def __init__(self):
        """Initialize the risk manager."""
        self.risks = self._identify_risks()
        self.mitigation_plans = self._create_mitigation_plans()
    
    def _identify_risks(self) -> List[Risk]:
        """Identify potential project risks."""
        risks = []
        
        # Technical risks
        risks.append(Risk(
            id='RISK001',
            title='YouTube API Rate Limiting',
            description='YouTube API may impose rate limits that could slow down data collection',
            level=RiskLevel.MEDIUM,
            probability=0.7,
            impact=0.6,
            mitigation_strategy='Implement rate limiting and caching mechanisms',
            owner='Back End Architect',
            status='identified'
        ))
        
        risks.append(Risk(
            id='RISK002',
            title='Google Sheets API Quota Exceeded',
            description='Google Sheets API may have quota limits that could prevent data writing',
            level=RiskLevel.MEDIUM,
            probability=0.5,
            impact=0.7,
            mitigation_strategy='Implement quota monitoring and batch processing',
            owner='Back End Architect',
            status='identified'
        ))
        
        # Security risks
        risks.append(Risk(
            id='RISK003',
            title='API Key Exposure',
            description='API keys could be exposed in logs or code, compromising security',
            level=RiskLevel.HIGH,
            probability=0.3,
            impact=0.9,
            mitigation_strategy='Implement secure key management and environment variables',
            owner='Security Engineer',
            status='identified'
        ))
        
        # Business risks
        risks.append(Risk(
            id='RISK004',
            title='User Adoption Low',
            description='Users may not adopt the tool due to complexity or lack of value',
            level=RiskLevel.MEDIUM,
            probability=0.4,
            impact=0.8,
            mitigation_strategy='Conduct user research and improve onboarding experience',
            owner='UX Designer',
            status='identified'
        ))
        
        # Performance risks
        risks.append(Risk(
            id='RISK005',
            title='System Performance Degradation',
            description='System performance may degrade with increased usage',
            level=RiskLevel.MEDIUM,
            probability=0.6,
            impact=0.5,
            mitigation_strategy='Implement performance monitoring and optimization',
            owner='Performance Engineer',
            status='identified'
        ))
        
        return risks
    
    def _create_mitigation_plans(self) -> Dict[str, Dict[str, Any]]:
        """Create mitigation plans for identified risks."""
        plans = {}
        
        plans['RISK001'] = {
            'strategy': 'Implement rate limiting and caching',
            'actions': [
                'Implement request queuing system',
                'Add caching layer for frequently accessed data',
                'Monitor API usage and implement backoff strategies',
                'Create fallback mechanisms for rate limit scenarios'
            ],
            'timeline': '2 weeks',
            'resources': ['Back End Architect', 'Lead Engineer'],
            'success_criteria': 'API requests stay within rate limits 95% of the time'
        }
        
        plans['RISK002'] = {
            'strategy': 'Implement quota monitoring and batch processing',
            'actions': [
                'Monitor Google Sheets API quota usage',
                'Implement batch processing for large data sets',
                'Add quota reset scheduling',
                'Create alert system for quota approaching limits'
            ],
            'timeline': '1 week',
            'resources': ['Back End Architect', 'DevOps Lead'],
            'success_criteria': 'No quota exceeded errors in production'
        }
        
        plans['RISK003'] = {
            'strategy': 'Implement secure key management',
            'actions': [
                'Use environment variables for all API keys',
                'Implement key rotation mechanisms',
                'Add key validation and monitoring',
                'Create secure key storage solution'
            ],
            'timeline': '1 week',
            'resources': ['Security Engineer', 'DevOps Lead'],
            'success_criteria': 'No API keys exposed in logs or code'
        }
        
        return plans
    
    def assess_risk_level(self, risk: Risk) -> RiskLevel:
        """Assess the overall risk level based on probability and impact."""
        risk_score = risk.probability * risk.impact
        
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_risk_dashboard(self) -> Dict[str, Any]:
        """Get risk dashboard with current risk status."""
        critical_risks = [r for r in self.risks if self.assess_risk_level(r) == RiskLevel.CRITICAL]
        high_risks = [r for r in self.risks if self.assess_risk_level(r) == RiskLevel.HIGH]
        medium_risks = [r for r in self.risks if self.assess_risk_level(r) == RiskLevel.MEDIUM]
        low_risks = [r for r in self.risks if self.assess_risk_level(r) == RiskLevel.LOW]
        
        return {
            'total_risks': len(self.risks),
            'critical_risks': len(critical_risks),
            'high_risks': len(high_risks),
            'medium_risks': len(medium_risks),
            'low_risks': len(low_risks),
            'risks_by_level': {
                'critical': [{'id': r.id, 'title': r.title} for r in critical_risks],
                'high': [{'id': r.id, 'title': r.title} for r in high_risks],
                'medium': [{'id': r.id, 'title': r.title} for r in medium_risks],
                'low': [{'id': r.id, 'title': r.title} for r in low_risks]
            },
            'mitigation_plans': self.mitigation_plans
        }
```

### Stakeholder Management
```python
# product/stakeholder_management.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class StakeholderType(Enum):
    """Stakeholder types."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    USER = "user"
    CUSTOMER = "customer"

@dataclass
class Stakeholder:
    """Represents a stakeholder."""
    id: str
    name: str
    type: StakeholderType
    role: str
    influence: str
    interest: str
    communication_preferences: List[str]
    concerns: List[str]

class StakeholderManager:
    """Manages stakeholders and their needs."""
    
    def __init__(self):
        """Initialize the stakeholder manager."""
        self.stakeholders = self._identify_stakeholders()
        self.communication_plans = self._create_communication_plans()
    
    def _identify_stakeholders(self) -> List[Stakeholder]:
        """Identify project stakeholders."""
        stakeholders = []
        
        # Internal stakeholders
        stakeholders.append(Stakeholder(
            id='STK001',
            name='Development Team',
            type=StakeholderType.INTERNAL,
            role='Build and maintain the product',
            influence='high',
            interest='high',
            communication_preferences=['Daily standups', 'Slack', 'Code reviews'],
            concerns=['Technical feasibility', 'Code quality', 'Timeline']
        ))
        
        stakeholders.append(Stakeholder(
            id='STK002',
            name='Product Owner',
            type=StakeholderType.INTERNAL,
            role='Define product requirements and priorities',
            influence='high',
            interest='high',
            communication_preferences=['Weekly reviews', 'Email', 'Meetings'],
            concerns=['User needs', 'Business value', 'Feature prioritization']
        ))
        
        # External stakeholders
        stakeholders.append(Stakeholder(
            id='STK003',
            name='YouTube Content Creators',
            type=StakeholderType.USER,
            role='Primary users of the product',
            influence='medium',
            interest='high',
            communication_preferences=['User surveys', 'Feedback forms', 'Support tickets'],
            concerns=['Ease of use', 'Data accuracy', 'Performance']
        ))
        
        stakeholders.append(Stakeholder(
            id='STK004',
            name='Data Analysts',
            type=StakeholderType.USER,
            role='Advanced users who need detailed data',
            influence='medium',
            interest='high',
            communication_preferences=['Technical documentation', 'API docs', 'Forums'],
            concerns=['Data quality', 'API access', 'Customization']
        ))
        
        stakeholders.append(Stakeholder(
            id='STK005',
            name='Marketing Managers',
            type=StakeholderType.CUSTOMER,
            role='Decision makers for tool adoption',
            influence='high',
            interest='medium',
            communication_preferences=['Executive summaries', 'Demos', 'ROI reports'],
            concerns=['ROI', 'Team productivity', 'Integration']
        ))
        
        return stakeholders
    
    def _create_communication_plans(self) -> Dict[str, Dict[str, Any]]:
        """Create communication plans for stakeholders."""
        plans = {}
        
        plans['STK001'] = {
            'frequency': 'Daily',
            'channels': ['Daily standups', 'Slack', 'Code reviews'],
            'content': [
                'Progress updates',
                'Technical decisions',
                'Blockers and issues',
                'Code quality metrics'
            ],
            'format': 'Interactive meetings and real-time chat'
        }
        
        plans['STK002'] = {
            'frequency': 'Weekly',
            'channels': ['Weekly reviews', 'Email', 'Meetings'],
            'content': [
                'Product roadmap updates',
                'Feature prioritization',
                'User feedback summary',
                'Business metrics'
            ],
            'format': 'Structured meetings with reports'
        }
        
        plans['STK003'] = {
            'frequency': 'Monthly',
            'channels': ['User surveys', 'Feedback forms', 'Support tickets'],
            'content': [
                'Feature announcements',
                'Usage tips and best practices',
                'User feedback requests',
                'Product updates'
            ],
            'format': 'Newsletters and in-app notifications'
        }
        
        return plans
    
    def get_stakeholder_matrix(self) -> Dict[str, Any]:
        """Get stakeholder influence-interest matrix."""
        matrix = {
            'high_influence_high_interest': [
                {'id': s.id, 'name': s.name, 'role': s.role}
                for s in self.stakeholders
                if s.influence == 'high' and s.interest == 'high'
            ],
            'high_influence_low_interest': [
                {'id': s.id, 'name': s.name, 'role': s.role}
                for s in self.stakeholders
                if s.influence == 'high' and s.interest == 'low'
            ],
            'low_influence_high_interest': [
                {'id': s.id, 'name': s.name, 'role': s.role}
                for s in self.stakeholders
                if s.influence == 'low' and s.interest == 'high'
            ],
            'low_influence_low_interest': [
                {'id': s.id, 'name': s.name, 'role': s.role}
                for s in self.stakeholders
                if s.influence == 'low' and s.interest == 'low'
            ]
        }
        
        return matrix
    
    def get_communication_schedule(self) -> Dict[str, Any]:
        """Get communication schedule for all stakeholders."""
        schedule = {}
        
        for stakeholder in self.stakeholders:
            plan = self.communication_plans.get(stakeholder.id, {})
            schedule[stakeholder.name] = {
                'frequency': plan.get('frequency', 'As needed'),
                'channels': plan.get('channels', []),
                'next_communication': self._calculate_next_communication(plan.get('frequency', 'As needed')),
                'content': plan.get('content', [])
            }
        
        return schedule
    
    def _calculate_next_communication(self, frequency: str) -> str:
        """Calculate next communication date based on frequency."""
        # This would contain actual date calculation logic
        # For now, return a mock value
        return '2024-01-15'
```

### Success Metrics

#### Product Metrics
- **User Adoption**: > 80% target user adoption
- **User Satisfaction**: > 4.5/5 user satisfaction score
- **Feature Usage**: > 70% feature adoption rate
- **Time to Value**: < 30 minutes time to first value

#### Project Metrics
- **On-time Delivery**: > 90% features delivered on time
- **Budget Adherence**: < 5% budget variance
- **Quality Gates**: > 95% quality gate pass rate
- **Risk Mitigation**: > 90% risk mitigation success rate

#### Team Metrics
- **Team Velocity**: Consistent velocity across sprints
- **Sprint Completion**: > 85% sprint completion rate
- **Defect Rate**: < 5% defect rate in production
- **Team Satisfaction**: > 4.0/5 team satisfaction score

### Collaboration Patterns

#### With Savant Architect
- Coordinate technical architecture decisions
- Ensure technical feasibility of product requirements
- Align product vision with technical capabilities

#### With Lead Engineer
- Coordinate development priorities
- Ensure code quality and performance
- Manage technical debt and refactoring

#### With UX Designer
- Coordinate user experience requirements
- Ensure user needs are met
- Align product vision with user experience

#### With QA Director
- Coordinate quality assurance strategies
- Ensure product quality standards
- Manage testing priorities and timelines
