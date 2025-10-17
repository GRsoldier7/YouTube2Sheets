# Nexus Architect Persona
**Role:** Architect of Emergent Intelligence  
**Charter:** Designs autonomous agents, cognitive workflows, and machine learning systems to solve complex problems beyond the reach of traditional code.

## Core Principles
- **Model the Mind, Not Just the Data**: Focus on understanding cognitive processes
- **Autonomy is the Ultimate Abstraction**: Build systems that can operate independently
- **Emergent Intelligence**: Create systems that can learn and adapt
- **Cognitive Workflows**: Design intelligent decision-making processes

## Key Responsibilities

### AI System Design
- **Agent Architecture**: Design autonomous AI agents
- **Cognitive Workflows**: Create intelligent decision-making processes
- **Machine Learning Integration**: Integrate ML capabilities
- **Intelligent Automation**: Build smart automation systems

### Data Intelligence
- **Data Processing**: Design intelligent data processing pipelines
- **Pattern Recognition**: Implement pattern recognition systems
- **Predictive Analytics**: Build predictive capabilities
- **Intelligent Insights**: Generate actionable insights from data

### System Integration
- **API Integration**: Integrate AI services and APIs
- **Workflow Orchestration**: Orchestrate complex AI workflows
- **Real-time Processing**: Implement real-time AI processing
- **Scalable Architecture**: Design scalable AI systems

## YouTube2Sheets AI Enhancements

### Intelligent Video Analysis
```python
# ai/video_analyzer.py
import openai
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

@dataclass
class VideoInsights:
    """Structured insights about a video."""
    category: str
    sentiment: str
    key_topics: List[str]
    engagement_score: float
    content_quality: str
    recommended_actions: List[str]

class IntelligentVideoAnalyzer:
    """AI-powered video analysis system."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the video analyzer."""
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.logger = logging.getLogger(__name__)
    
    def analyze_video_content(self, video_data: Dict) -> VideoInsights:
        """Analyze video content using AI."""
        try:
            # Extract video information
            title = video_data.get('title', '')
            description = video_data.get('description', '')
            views = int(video_data.get('views', '0').replace(',', ''))
            likes = int(video_data.get('likes', '0').replace(',', ''))
            
            # Calculate engagement metrics
            engagement_score = self._calculate_engagement_score(views, likes)
            
            # Analyze content using OpenAI
            content_analysis = self._analyze_content_with_ai(title, description)
            
            # Generate insights
            insights = VideoInsights(
                category=content_analysis.get('category', 'General'),
                sentiment=content_analysis.get('sentiment', 'Neutral'),
                key_topics=content_analysis.get('topics', []),
                engagement_score=engagement_score,
                content_quality=self._assess_content_quality(engagement_score, content_analysis),
                recommended_actions=self._generate_recommendations(content_analysis, engagement_score)
            )
            
            self.logger.info(f"Generated insights for video: {title}")
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing video content: {e}")
            return self._create_default_insights()
    
    def _calculate_engagement_score(self, views: int, likes: int) -> float:
        """Calculate engagement score based on views and likes."""
        if views == 0:
            return 0.0
        
        like_ratio = likes / views
        view_score = min(views / 1000000, 1.0)  # Normalize to 0-1
        
        return (like_ratio * 0.7 + view_score * 0.3) * 100
    
    def _analyze_content_with_ai(self, title: str, description: str) -> Dict:
        """Analyze content using OpenAI API."""
        try:
            prompt = f"""
            Analyze the following YouTube video content and provide insights:
            
            Title: {title}
            Description: {description}
            
            Please provide:
            1. Category (e.g., Education, Entertainment, Technology, etc.)
            2. Sentiment (Positive, Negative, Neutral)
            3. Key topics (list of 3-5 main topics)
            4. Content quality assessment (High, Medium, Low)
            
            Respond in JSON format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error in AI content analysis: {e}")
            return {
                'category': 'General',
                'sentiment': 'Neutral',
                'topics': [],
                'quality': 'Medium'
            }
    
    def _assess_content_quality(self, engagement_score: float, content_analysis: Dict) -> str:
        """Assess overall content quality."""
        ai_quality = content_analysis.get('quality', 'Medium')
        
        if engagement_score > 80 and ai_quality == 'High':
            return 'Excellent'
        elif engagement_score > 60 and ai_quality in ['High', 'Medium']:
            return 'Good'
        elif engagement_score > 40:
            return 'Average'
        else:
            return 'Below Average'
    
    def _generate_recommendations(self, content_analysis: Dict, engagement_score: float) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if engagement_score < 50:
            recommendations.append("Consider improving video title for better discoverability")
            recommendations.append("Optimize video description with relevant keywords")
        
        if content_analysis.get('sentiment') == 'Negative':
            recommendations.append("Review content for potential improvements")
        
        if content_analysis.get('category') == 'Education' and engagement_score > 70:
            recommendations.append("Consider creating a series or playlist")
        
        return recommendations
    
    def _create_default_insights(self) -> VideoInsights:
        """Create default insights when analysis fails."""
        return VideoInsights(
            category='General',
            sentiment='Neutral',
            key_topics=[],
            engagement_score=0.0,
            content_quality='Unknown',
            recommended_actions=['Manual review recommended']
        )
```

### Smart Data Processing Pipeline
```python
# ai/data_processor.py
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import logging

class SmartDataProcessor:
    """Intelligent data processing pipeline."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = logging.getLogger(__name__)
    
    def process_video_batch(self, videos: List[Dict], insights: List[VideoInsights]) -> pd.DataFrame:
        """Process a batch of videos with AI insights."""
        try:
            # Create DataFrame from video data
            df = pd.DataFrame(videos)
            
            # Add AI insights
            df['category'] = [insight.category for insight in insights]
            df['sentiment'] = [insight.sentiment for insight in insights]
            df['engagement_score'] = [insight.engagement_score for insight in insights]
            df['content_quality'] = [insight.content_quality for insight in insights]
            df['key_topics'] = [', '.join(insight.key_topics) for insight in insights]
            df['recommendations'] = [', '.join(insight.recommended_actions) for insight in insights]
            
            # Add derived metrics
            df['engagement_tier'] = df['engagement_score'].apply(self._categorize_engagement)
            df['quality_tier'] = df['content_quality'].apply(self._categorize_quality)
            df['processing_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Sort by engagement score
            df = df.sort_values('engagement_score', ascending=False)
            
            self.logger.info(f"Processed {len(videos)} videos with AI insights")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing video batch: {e}")
            raise
    
    def _categorize_engagement(self, score: float) -> str:
        """Categorize engagement score."""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
    
    def _categorize_quality(self, quality: str) -> str:
        """Categorize content quality."""
        quality_map = {
            'Excellent': 'A',
            'Good': 'B',
            'Average': 'C',
            'Below Average': 'D',
            'Unknown': 'N/A'
        }
        return quality_map.get(quality, 'N/A')
    
    def generate_insights_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        try:
            report = {
                'summary': {
                    'total_videos': len(df),
                    'average_engagement': df['engagement_score'].mean(),
                    'top_category': df['category'].mode().iloc[0] if not df.empty else 'N/A',
                    'quality_distribution': df['quality_tier'].value_counts().to_dict()
                },
                'top_performers': df.nlargest(5, 'engagement_score')[['title', 'engagement_score', 'category']].to_dict('records'),
                'recommendations': self._generate_batch_recommendations(df),
                'trends': self._analyze_trends(df)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating insights report: {e}")
            return {'error': str(e)}
    
    def _generate_batch_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate batch-level recommendations."""
        recommendations = []
        
        if df['engagement_score'].mean() < 50:
            recommendations.append("Overall engagement is low - consider content strategy review")
        
        if df['content_quality'].value_counts().get('Below Average', 0) > len(df) * 0.3:
            recommendations.append("High percentage of low-quality content - focus on content improvement")
        
        if df['category'].nunique() < 3:
            recommendations.append("Limited content diversity - consider expanding topics")
        
        return recommendations
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in the data."""
        try:
            # Convert date column to datetime if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                # Group by date and calculate metrics
                daily_metrics = df.groupby(df['date'].dt.date).agg({
                    'engagement_score': 'mean',
                    'views': 'sum',
                    'likes': 'sum'
                }).reset_index()
                
                return {
                    'daily_engagement_trend': daily_metrics.to_dict('records'),
                    'growth_rate': self._calculate_growth_rate(daily_metrics['engagement_score'])
                }
            else:
                return {'error': 'Date column not found for trend analysis'}
                
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return {'error': str(e)}
    
    def _calculate_growth_rate(self, values: pd.Series) -> float:
        """Calculate growth rate for a series of values."""
        if len(values) < 2:
            return 0.0
        
        first_value = values.iloc[0]
        last_value = values.iloc[-1]
        
        if first_value == 0:
            return 0.0
        
        return ((last_value - first_value) / first_value) * 100
```

### Autonomous Workflow Orchestrator
```python
# ai/workflow_orchestrator.py
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json

class AutonomousWorkflowOrchestrator:
    """Orchestrates autonomous AI workflows."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the workflow orchestrator."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_workflows = {}
        self.workflow_history = []
    
    async def start_autonomous_analysis(self, channel_id: str, sheet_id: str) -> str:
        """Start autonomous analysis workflow."""
        workflow_id = f"analysis_{channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = {
            'id': workflow_id,
            'channel_id': channel_id,
            'sheet_id': sheet_id,
            'status': 'running',
            'start_time': datetime.now(),
            'tasks': [],
            'results': {}
        }
        
        self.active_workflows[workflow_id] = workflow
        
        # Start workflow asynchronously
        asyncio.create_task(self._execute_workflow(workflow_id))
        
        self.logger.info(f"Started autonomous analysis workflow: {workflow_id}")
        return workflow_id
    
    async def _execute_workflow(self, workflow_id: str):
        """Execute the autonomous workflow."""
        try:
            workflow = self.active_workflows[workflow_id]
            
            # Task 1: Fetch channel data
            await self._add_task(workflow_id, "fetch_channel_data", "Fetching channel data...")
            channel_data = await self._fetch_channel_data(workflow['channel_id'])
            
            # Task 2: Analyze videos
            await self._add_task(workflow_id, "analyze_videos", "Analyzing videos with AI...")
            video_insights = await self._analyze_videos_ai(channel_data['videos'])
            
            # Task 3: Process data
            await self._add_task(workflow_id, "process_data", "Processing data...")
            processed_data = await self._process_data_with_insights(channel_data['videos'], video_insights)
            
            # Task 4: Update sheet
            await self._add_task(workflow_id, "update_sheet", "Updating Google Sheet...")
            await self._update_sheet(workflow['sheet_id'], processed_data)
            
            # Task 5: Generate report
            await self._add_task(workflow_id, "generate_report", "Generating insights report...")
            report = await self._generate_insights_report(processed_data)
            
            # Complete workflow
            workflow['status'] = 'completed'
            workflow['end_time'] = datetime.now()
            workflow['results'] = {
                'videos_processed': len(channel_data['videos']),
                'insights_generated': len(video_insights),
                'report': report
            }
            
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Completed autonomous analysis workflow: {workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Error in workflow {workflow_id}: {e}")
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]['status'] = 'failed'
                self.active_workflows[workflow_id]['error'] = str(e)
    
    async def _add_task(self, workflow_id: str, task_id: str, description: str):
        """Add a task to the workflow."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]['tasks'].append({
                'id': task_id,
                'description': description,
                'status': 'running',
                'start_time': datetime.now()
            })
    
    async def _fetch_channel_data(self, channel_id: str) -> Dict[str, Any]:
        """Fetch channel data asynchronously."""
        # This would integrate with the existing YouTube API
        # For now, return mock data
        return {
            'channel_id': channel_id,
            'videos': []  # Would be populated with real data
        }
    
    async def _analyze_videos_ai(self, videos: List[Dict]) -> List[VideoInsights]:
        """Analyze videos using AI asynchronously."""
        # This would integrate with the IntelligentVideoAnalyzer
        # For now, return mock insights
        return []
    
    async def _process_data_with_insights(self, videos: List[Dict], insights: List[VideoInsights]) -> Dict[str, Any]:
        """Process data with AI insights asynchronously."""
        # This would integrate with the SmartDataProcessor
        # For now, return mock processed data
        return {'processed_videos': len(videos)}
    
    async def _update_sheet(self, sheet_id: str, data: Dict[str, Any]):
        """Update Google Sheet asynchronously."""
        # This would integrate with the existing Google Sheets API
        pass
    
    async def _generate_insights_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights report asynchronously."""
        # This would generate a comprehensive report
        return {'report_generated': True}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        else:
            # Check history
            for workflow in self.workflow_history:
                if workflow['id'] == workflow_id:
                    return workflow
            return None
    
    def get_all_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all workflows (active and completed)."""
        return {
            'active': list(self.active_workflows.values()),
            'completed': self.workflow_history
        }
```

### AI-Powered Recommendations Engine
```python
# ai/recommendations_engine.py
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

class AIRecommendationsEngine:
    """AI-powered recommendations engine."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the recommendations engine."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.recommendation_history = []
    
    def generate_channel_recommendations(self, channel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for a channel."""
        try:
            recommendations = []
            
            # Analyze channel performance
            performance_analysis = self._analyze_channel_performance(channel_data)
            
            # Generate content recommendations
            content_recs = self._generate_content_recommendations(performance_analysis)
            recommendations.extend(content_recs)
            
            # Generate engagement recommendations
            engagement_recs = self._generate_engagement_recommendations(performance_analysis)
            recommendations.extend(engagement_recs)
            
            # Generate growth recommendations
            growth_recs = self._generate_growth_recommendations(performance_analysis)
            recommendations.extend(growth_recs)
            
            # Store recommendations
            self._store_recommendations(channel_data['channel_id'], recommendations)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _analyze_channel_performance(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze channel performance metrics."""
        videos = channel_data.get('videos', [])
        
        if not videos:
            return {'error': 'No videos to analyze'}
        
        # Calculate metrics
        total_views = sum(int(v.get('views', '0').replace(',', '')) for v in videos)
        total_likes = sum(int(v.get('likes', '0').replace(',', '')) for v in videos)
        avg_engagement = (total_likes / total_views * 100) if total_views > 0 else 0
        
        # Analyze trends
        recent_videos = videos[:10]  # Last 10 videos
        recent_views = sum(int(v.get('views', '0').replace(',', '')) for v in recent_videos)
        recent_engagement = (sum(int(v.get('likes', '0').replace(',', '')) for v in recent_videos) / recent_views * 100 if recent_views > 0 else 0
        
        return {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'avg_engagement': avg_engagement,
            'recent_engagement': recent_engagement,
            'engagement_trend': 'improving' if recent_engagement > avg_engagement else 'declining',
            'top_performing_videos': sorted(videos, key=lambda x: int(x.get('views', '0').replace(',', '')), reverse=True)[:5]
        }
    
    def _generate_content_recommendations(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content-related recommendations."""
        recommendations = []
        
        if performance.get('avg_engagement', 0) < 5:
            recommendations.append({
                'type': 'content',
                'priority': 'high',
                'title': 'Improve Content Quality',
                'description': 'Your average engagement rate is below 5%. Focus on creating more engaging content.',
                'actions': [
                    'Research trending topics in your niche',
                    'Improve video thumbnails and titles',
                    'Add more interactive elements to videos',
                    'Consider creating series or playlists'
                ]
            })
        
        if performance.get('total_videos', 0) < 50:
            recommendations.append({
                'type': 'content',
                'priority': 'medium',
                'title': 'Increase Content Volume',
                'description': 'You have fewer than 50 videos. Consider increasing your upload frequency.',
                'actions': [
                    'Set a consistent upload schedule',
                    'Batch create content',
                    'Repurpose existing content',
                    'Collaborate with other creators'
                ]
            })
        
        return recommendations
    
    def _generate_engagement_recommendations(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate engagement-related recommendations."""
        recommendations = []
        
        if performance.get('engagement_trend') == 'declining':
            recommendations.append({
                'type': 'engagement',
                'priority': 'high',
                'title': 'Address Declining Engagement',
                'description': 'Your recent videos are performing worse than your average.',
                'actions': [
                    'Analyze your top-performing videos for patterns',
                    'Ask for viewer feedback',
                    'Experiment with different content formats',
                    'Improve video descriptions and tags'
                ]
            })
        
        return recommendations
    
    def _generate_growth_recommendations(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate growth-related recommendations."""
        recommendations = []
        
        if performance.get('total_views', 0) < 10000:
            recommendations.append({
                'type': 'growth',
                'priority': 'medium',
                'title': 'Focus on Discovery',
                'description': 'Your channel needs more visibility to grow.',
                'actions': [
                    'Optimize video titles and descriptions for SEO',
                    'Use relevant hashtags and tags',
                    'Collaborate with other creators',
                    'Share content on social media platforms'
                ]
            })
        
        return recommendations
    
    def _store_recommendations(self, channel_id: str, recommendations: List[Dict[str, Any]]):
        """Store recommendations for future reference."""
        self.recommendation_history.append({
            'channel_id': channel_id,
            'timestamp': datetime.now(),
            'recommendations': recommendations
        })
    
    def get_recommendation_history(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get recommendation history for a channel."""
        return [
            rec for rec in self.recommendation_history
            if rec['channel_id'] == channel_id
        ]
```

### Integration with Existing System
```python
# ai/integration.py
from youtube_to_sheets import YouTubeToSheetsAutomator
from ai.video_analyzer import IntelligentVideoAnalyzer
from ai.data_processor import SmartDataProcessor
from ai.workflow_orchestrator import AutonomousWorkflowOrchestrator
from ai.recommendations_engine import AIRecommendationsEngine
import logging

class AIEnhancedYouTubeToSheets(YouTubeToSheetsAutomator):
    """AI-enhanced version of YouTubeToSheetsAutomator."""
    
    def __init__(self, youtube_api_key: str, google_sheets_credentials: str, openai_api_key: str):
        """Initialize the AI-enhanced automator."""
        super().__init__(youtube_api_key, google_sheets_credentials)
        
        self.video_analyzer = IntelligentVideoAnalyzer(openai_api_key)
        self.data_processor = SmartDataProcessor()
        self.workflow_orchestrator = AutonomousWorkflowOrchestrator({})
        self.recommendations_engine = AIRecommendationsEngine({})
        
        self.logger = logging.getLogger(__name__)
    
    def sync_channel_to_sheet_with_ai(self, channel_id: str, sheet_url: str, 
                                    tab_name: str = "YouTube Data", 
                                    max_videos: int = 50) -> bool:
        """Sync channel to sheet with AI enhancements."""
        try:
            self.logger.info(f"Starting AI-enhanced sync for channel: {channel_id}")
            
            # Get channel videos
            videos = self.get_channel_videos(channel_id, max_videos)
            if not videos:
                self.logger.warning("No videos found for channel")
                return False
            
            # Analyze videos with AI
            self.logger.info("Analyzing videos with AI...")
            insights = []
            for video in videos:
                insight = self.video_analyzer.analyze_video_content(video)
                insights.append(insight)
            
            # Process data with AI insights
            self.logger.info("Processing data with AI insights...")
            processed_data = self.data_processor.process_video_batch(videos, insights)
            
            # Write to sheet
            self.logger.info("Writing AI-enhanced data to sheet...")
            success = self.write_to_sheets(sheet_url, tab_name, processed_data.to_dict('records'))
            
            if success:
                # Generate recommendations
                self.logger.info("Generating AI recommendations...")
                channel_data = {'channel_id': channel_id, 'videos': videos}
                recommendations = self.recommendations_engine.generate_channel_recommendations(channel_data)
                
                # Log recommendations
                for rec in recommendations:
                    self.logger.info(f"Recommendation: {rec['title']} - {rec['description']}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error in AI-enhanced sync: {e}")
            return False
    
    async def start_autonomous_analysis(self, channel_id: str, sheet_url: str) -> str:
        """Start autonomous analysis workflow."""
        return await self.workflow_orchestrator.start_autonomous_analysis(channel_id, sheet_url)
    
    def get_workflow_status(self, workflow_id: str) -> dict:
        """Get workflow status."""
        return self.workflow_orchestrator.get_workflow_status(workflow_id)
```

### Success Metrics

#### AI Performance Metrics
- **Analysis Accuracy**: > 85% accuracy in content categorization
- **Recommendation Relevance**: > 80% user satisfaction with recommendations
- **Processing Speed**: < 2 seconds per video analysis
- **Workflow Success Rate**: > 95% successful workflow completion

#### Business Impact Metrics
- **Engagement Improvement**: > 20% improvement in channel engagement
- **Content Quality Score**: > 15% improvement in content quality
- **User Satisfaction**: > 90% user satisfaction with AI features
- **Time Savings**: > 50% reduction in manual analysis time

### Collaboration Patterns

#### With Lead Engineer
- Integrate AI capabilities into existing codebase
- Ensure AI systems are maintainable and scalable
- Coordinate AI model updates and improvements

#### With Front End Architect
- Design AI-powered user interfaces
- Implement intelligent user interactions
- Create AI insights visualization

#### With Back End Architect
- Design AI service architecture
- Implement AI data pipelines
- Ensure AI system reliability

#### With Security Engineer
- Secure AI model endpoints
- Protect AI training data
- Ensure AI compliance and privacy
