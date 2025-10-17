# Data Engineer Persona
**Role:** Master of Data Flow  
**Charter:** Designs and implements robust data pipelines, ensures data quality, and optimizes data processing for maximum efficiency and reliability.

## Core Principles
- **Data Quality First**: Ensure data integrity and accuracy at every step
- **Scalable Architecture**: Design systems that can handle growing data volumes
- **Real-time Processing**: Enable real-time data processing when needed
- **Data Lineage**: Maintain clear data lineage and provenance

## Key Responsibilities

### Data Pipeline Design
- **ETL/ELT Processes**: Design efficient data extraction, transformation, and loading
- **Data Flow Architecture**: Create robust data flow architectures
- **Data Integration**: Integrate data from multiple sources
- **Data Transformation**: Transform data for optimal storage and processing

### Data Quality Assurance
- **Data Validation**: Implement comprehensive data validation
- **Data Cleansing**: Clean and standardize data
- **Data Monitoring**: Monitor data quality metrics
- **Data Governance**: Ensure data governance and compliance

### Performance Optimization
- **Query Optimization**: Optimize data queries for performance
- **Caching Strategies**: Implement effective caching strategies
- **Data Partitioning**: Partition data for optimal performance
- **Resource Management**: Optimize resource usage

## YouTube2Sheets Data Engineering

### Data Pipeline Architecture
```python
# data/pipeline.py
import logging
from typing import Dict, List, Any, Optional, Iterator
from datetime import datetime, timedelta
import pandas as pd
import json
from dataclasses import dataclass
from enum import Enum

class DataStage(Enum):
    """Data processing stages."""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    CLEAN = "clean"

@dataclass
class DataRecord:
    """Represents a single data record."""
    id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    stage: DataStage
    quality_score: float = 0.0

class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data pipeline."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stages = {
            DataStage.EXTRACT: self._extract_stage,
            DataStage.TRANSFORM: self._transform_stage,
            DataStage.LOAD: self._load_stage,
            DataStage.VALIDATE: self._validate_stage,
            DataStage.CLEAN: self._clean_stage
        }
        self.data_quality_rules = self._load_quality_rules()
    
    def process_data(self, source_data: List[Dict[str, Any]], 
                    target_system: str) -> Dict[str, Any]:
        """Process data through the complete pipeline."""
        try:
            self.logger.info("Starting data pipeline processing")
            
            # Initialize processing context
            context = {
                'source_data': source_data,
                'target_system': target_system,
                'start_time': datetime.now(),
                'records_processed': 0,
                'errors': [],
                'quality_metrics': {}
            }
            
            # Process through each stage
            for stage in DataStage:
                self.logger.info(f"Processing stage: {stage.value}")
                context = self.stages[stage](context)
                
                if context.get('errors'):
                    self.logger.error(f"Errors in stage {stage.value}: {context['errors']}")
                    break
            
            # Generate processing report
            report = self._generate_processing_report(context)
            
            self.logger.info(f"Data pipeline processing completed: {report['status']}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error in data pipeline processing: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _extract_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from source."""
        try:
            source_data = context['source_data']
            extracted_records = []
            
            for item in source_data:
                record = DataRecord(
                    id=self._generate_record_id(item),
                    data=item,
                    metadata={
                        'source': 'youtube_api',
                        'extraction_time': datetime.now().isoformat(),
                        'record_type': 'video'
                    },
                    timestamp=datetime.now(),
                    stage=DataStage.EXTRACT
                )
                extracted_records.append(record)
            
            context['extracted_records'] = extracted_records
            context['records_processed'] = len(extracted_records)
            
            self.logger.info(f"Extracted {len(extracted_records)} records")
            return context
            
        except Exception as e:
            context['errors'].append(f"Extract stage error: {e}")
            return context
    
    def _transform_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to business rules."""
        try:
            extracted_records = context.get('extracted_records', [])
            transformed_records = []
            
            for record in extracted_records:
                # Apply transformations
                transformed_data = self._apply_transformations(record.data)
                
                # Create transformed record
                transformed_record = DataRecord(
                    id=record.id,
                    data=transformed_data,
                    metadata={
                        **record.metadata,
                        'transformation_time': datetime.now().isoformat(),
                        'transformations_applied': self._get_applied_transformations()
                    },
                    timestamp=datetime.now(),
                    stage=DataStage.TRANSFORM,
                    quality_score=record.quality_score
                )
                
                transformed_records.append(transformed_record)
            
            context['transformed_records'] = transformed_records
            
            self.logger.info(f"Transformed {len(transformed_records)} records")
            return context
            
        except Exception as e:
            context['errors'].append(f"Transform stage error: {e}")
            return context
    
    def _load_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load data into target system."""
        try:
            transformed_records = context.get('transformed_records', [])
            target_system = context['target_system']
            
            # Convert records to target format
            target_data = self._convert_to_target_format(transformed_records)
            
            # Load into target system
            load_result = self._load_to_target_system(target_data, target_system)
            
            context['load_result'] = load_result
            context['records_loaded'] = len(transformed_records)
            
            self.logger.info(f"Loaded {len(transformed_records)} records to {target_system}")
            return context
            
        except Exception as e:
            context['errors'].append(f"Load stage error: {e}")
            return context
    
    def _validate_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality."""
        try:
            records = context.get('transformed_records', [])
            validation_results = []
            
            for record in records:
                validation_result = self._validate_record(record)
                validation_results.append(validation_result)
                
                # Update quality score
                record.quality_score = validation_result['quality_score']
            
            context['validation_results'] = validation_results
            context['quality_metrics'] = self._calculate_quality_metrics(validation_results)
            
            self.logger.info(f"Validated {len(records)} records")
            return context
            
        except Exception as e:
            context['errors'].append(f"Validation stage error: {e}")
            return context
    
    def _clean_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize data."""
        try:
            records = context.get('transformed_records', [])
            cleaned_records = []
            
            for record in records:
                cleaned_data = self._clean_record_data(record.data)
                
                cleaned_record = DataRecord(
                    id=record.id,
                    data=cleaned_data,
                    metadata={
                        **record.metadata,
                        'cleaning_time': datetime.now().isoformat(),
                        'cleaning_applied': self._get_applied_cleaning()
                    },
                    timestamp=datetime.now(),
                    stage=DataStage.CLEAN,
                    quality_score=record.quality_score
                )
                
                cleaned_records.append(cleaned_record)
            
            context['cleaned_records'] = cleaned_records
            
            self.logger.info(f"Cleaned {len(cleaned_records)} records")
            return context
            
        except Exception as e:
            context['errors'].append(f"Clean stage error: {e}")
            return context
    
    def _generate_record_id(self, item: Dict[str, Any]) -> str:
        """Generate unique record ID."""
        return f"video_{item.get('id', {}).get('videoId', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data transformations."""
        transformed = data.copy()
        
        # Standardize date format
        if 'publishedAt' in transformed:
            transformed['publishedAt'] = self._standardize_date(transformed['publishedAt'])
        
        # Convert numeric fields
        if 'viewCount' in transformed:
            transformed['viewCount'] = self._convert_to_int(transformed['viewCount'])
        
        if 'likeCount' in transformed:
            transformed['likeCount'] = self._convert_to_int(transformed['likeCount'])
        
        # Add derived fields
        transformed['engagement_rate'] = self._calculate_engagement_rate(transformed)
        transformed['content_duration_seconds'] = self._parse_duration_to_seconds(transformed.get('duration', 'PT0S'))
        
        return transformed
    
    def _standardize_date(self, date_str: str) -> str:
        """Standardize date format."""
        try:
            from dateutil import parser
            parsed_date = parser.parse(date_str)
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
    
    def _convert_to_int(self, value: str) -> int:
        """Convert string to integer, handling commas."""
        try:
            return int(value.replace(',', ''))
        except:
            return 0
    
    def _calculate_engagement_rate(self, data: Dict[str, Any]) -> float:
        """Calculate engagement rate."""
        views = data.get('viewCount', 0)
        likes = data.get('likeCount', 0)
        
        if views == 0:
            return 0.0
        
        return (likes / views) * 100
    
    def _parse_duration_to_seconds(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _get_applied_transformations(self) -> List[str]:
        """Get list of applied transformations."""
        return [
            'date_standardization',
            'numeric_conversion',
            'engagement_rate_calculation',
            'duration_parsing'
        ]
    
    def _convert_to_target_format(self, records: List[DataRecord]) -> List[Dict[str, Any]]:
        """Convert records to target system format."""
        target_data = []
        
        for record in records:
            target_record = {
                'id': record.id,
                'data': record.data,
                'metadata': record.metadata,
                'quality_score': record.quality_score,
                'timestamp': record.timestamp.isoformat()
            }
            target_data.append(target_record)
        
        return target_data
    
    def _load_to_target_system(self, data: List[Dict[str, Any]], target_system: str) -> Dict[str, Any]:
        """Load data into target system."""
        # This would contain the actual loading logic
        # For now, return a mock result
        return {
            'success': True,
            'records_loaded': len(data),
            'target_system': target_system,
            'load_time': datetime.now().isoformat()
        }
    
    def _validate_record(self, record: DataRecord) -> Dict[str, Any]:
        """Validate a single record."""
        validation_result = {
            'record_id': record.id,
            'quality_score': 0.0,
            'validation_errors': [],
            'validation_warnings': []
        }
        
        # Apply quality rules
        for rule in self.data_quality_rules:
            rule_result = rule.validate(record.data)
            
            if rule_result['passed']:
                validation_result['quality_score'] += rule_result['score']
            else:
                validation_result['validation_errors'].extend(rule_result['errors'])
        
        # Normalize quality score
        validation_result['quality_score'] = min(validation_result['quality_score'] / len(self.data_quality_rules), 1.0)
        
        return validation_result
    
    def _calculate_quality_metrics(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall quality metrics."""
        if not validation_results:
            return {}
        
        total_records = len(validation_results)
        avg_quality_score = sum(r['quality_score'] for r in validation_results) / total_records
        
        records_with_errors = len([r for r in validation_results if r['validation_errors']])
        records_with_warnings = len([r for r in validation_results if r['validation_warnings']])
        
        return {
            'total_records': total_records,
            'average_quality_score': avg_quality_score,
            'records_with_errors': records_with_errors,
            'records_with_warnings': records_with_warnings,
            'error_rate': records_with_errors / total_records,
            'warning_rate': records_with_warnings / total_records
        }
    
    def _clean_record_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean record data."""
        cleaned = data.copy()
        
        # Remove null values
        cleaned = {k: v for k, v in cleaned.items() if v is not None}
        
        # Standardize text fields
        for key in ['title', 'description', 'channelTitle']:
            if key in cleaned and isinstance(cleaned[key], str):
                cleaned[key] = cleaned[key].strip()
        
        return cleaned
    
    def _get_applied_cleaning(self) -> List[str]:
        """Get list of applied cleaning operations."""
        return [
            'null_value_removal',
            'text_standardization',
            'whitespace_trimming'
        ]
    
    def _load_quality_rules(self) -> List[Any]:
        """Load data quality rules."""
        # This would load actual quality rules
        # For now, return empty list
        return []
    
    def _generate_processing_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processing report."""
        return {
            'status': 'success' if not context.get('errors') else 'failed',
            'records_processed': context.get('records_processed', 0),
            'records_loaded': context.get('records_loaded', 0),
            'processing_time': (datetime.now() - context['start_time']).total_seconds(),
            'quality_metrics': context.get('quality_metrics', {}),
            'errors': context.get('errors', [])
        }
```

### Data Quality Framework
```python
# data/quality.py
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class QualityRule:
    """Represents a data quality rule."""
    name: str
    description: str
    weight: float
    validator: 'DataValidator'

class DataValidator(ABC):
    """Abstract base class for data validators."""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data and return result."""
        pass

class RequiredFieldValidator(DataValidator):
    """Validates that required fields are present."""
    
    def __init__(self, required_fields: List[str]):
        """Initialize with required fields."""
        self.required_fields = required_fields
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required fields."""
        missing_fields = [field for field in self.required_fields if field not in data or not data[field]]
        
        return {
            'passed': len(missing_fields) == 0,
            'score': 1.0 if len(missing_fields) == 0 else 0.0,
            'errors': [f"Missing required field: {field}" for field in missing_fields]
        }

class DataTypeValidator(DataValidator):
    """Validates data types."""
    
    def __init__(self, field_types: Dict[str, type]):
        """Initialize with field type mappings."""
        self.field_types = field_types
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data types."""
        errors = []
        
        for field, expected_type in self.field_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Field {field} has wrong type. Expected {expected_type.__name__}, got {type(data[field]).__name__}")
        
        return {
            'passed': len(errors) == 0,
            'score': 1.0 if len(errors) == 0 else 0.0,
            'errors': errors
        }

class RangeValidator(DataValidator):
    """Validates numeric ranges."""
    
    def __init__(self, field_ranges: Dict[str, tuple]):
        """Initialize with field range mappings."""
        self.field_ranges = field_ranges
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate numeric ranges."""
        errors = []
        
        for field, (min_val, max_val) in self.field_ranges.items():
            if field in data and isinstance(data[field], (int, float)):
                if not (min_val <= data[field] <= max_val):
                    errors.append(f"Field {field} value {data[field]} is outside range [{min_val}, {max_val}]")
        
        return {
            'passed': len(errors) == 0,
            'score': 1.0 if len(errors) == 0 else 0.0,
            'errors': errors
        }

class DataQualityManager:
    """Manages data quality rules and validation."""
    
    def __init__(self):
        """Initialize the data quality manager."""
        self.logger = logging.getLogger(__name__)
        self.quality_rules = self._initialize_quality_rules()
    
    def _initialize_quality_rules(self) -> List[QualityRule]:
        """Initialize data quality rules."""
        rules = []
        
        # Required fields rule
        required_fields = ['id', 'title', 'channelTitle', 'publishedAt']
        rules.append(QualityRule(
            name='required_fields',
            description='All required fields must be present',
            weight=0.3,
            validator=RequiredFieldValidator(required_fields)
        ))
        
        # Data types rule
        field_types = {
            'viewCount': int,
            'likeCount': int,
            'engagement_rate': float
        }
        rules.append(QualityRule(
            name='data_types',
            description='Data types must match expected types',
            weight=0.2,
            validator=DataTypeValidator(field_types)
        ))
        
        # Range validation rule
        field_ranges = {
            'engagement_rate': (0.0, 100.0),
            'viewCount': (0, 1000000000),
            'likeCount': (0, 100000000)
        }
        rules.append(QualityRule(
            name='ranges',
            description='Numeric fields must be within valid ranges',
            weight=0.2,
            validator=RangeValidator(field_ranges)
        ))
        
        return rules
    
    def validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data against quality rules."""
        validation_results = []
        
        for record in data:
            record_validation = {
                'record_id': record.get('id', 'unknown'),
                'quality_score': 0.0,
                'validation_errors': [],
                'validation_warnings': []
            }
            
            for rule in self.quality_rules:
                rule_result = rule.validator.validate(record)
                
                if rule_result['passed']:
                    record_validation['quality_score'] += rule_result['score'] * rule.weight
                else:
                    record_validation['validation_errors'].extend(rule_result['errors'])
            
            validation_results.append(record_validation)
        
        # Calculate overall quality metrics
        total_records = len(validation_results)
        avg_quality_score = sum(r['quality_score'] for r in validation_results) / total_records
        records_with_errors = len([r for r in validation_results if r['validation_errors']])
        
        return {
            'total_records': total_records,
            'average_quality_score': avg_quality_score,
            'records_with_errors': records_with_errors,
            'error_rate': records_with_errors / total_records,
            'validation_results': validation_results
        }
```

### Data Monitoring System
```python
# data/monitoring.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd

class DataMonitor:
    """Monitors data quality and pipeline performance."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data monitor."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.monitoring_data = []
        self.alert_thresholds = config.get('alert_thresholds', {})
    
    def monitor_pipeline_execution(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor pipeline execution and generate alerts."""
        try:
            monitoring_record = {
                'timestamp': datetime.now().isoformat(),
                'pipeline_id': pipeline_result.get('pipeline_id', 'unknown'),
                'status': pipeline_result.get('status', 'unknown'),
                'records_processed': pipeline_result.get('records_processed', 0),
                'processing_time': pipeline_result.get('processing_time', 0),
                'quality_score': pipeline_result.get('quality_metrics', {}).get('average_quality_score', 0),
                'error_rate': pipeline_result.get('quality_metrics', {}).get('error_rate', 0)
            }
            
            self.monitoring_data.append(monitoring_record)
            
            # Check for alerts
            alerts = self._check_alerts(monitoring_record)
            
            # Generate monitoring report
            report = {
                'monitoring_record': monitoring_record,
                'alerts': alerts,
                'trends': self._analyze_trends(),
                'recommendations': self._generate_recommendations(monitoring_record)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error in pipeline monitoring: {e}")
            return {'error': str(e)}
    
    def _check_alerts(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        
        # Check processing time
        if record['processing_time'] > self.alert_thresholds.get('max_processing_time', 300):
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'message': f"Processing time exceeded threshold: {record['processing_time']}s",
                'timestamp': record['timestamp']
            })
        
        # Check quality score
        if record['quality_score'] < self.alert_thresholds.get('min_quality_score', 0.8):
            alerts.append({
                'type': 'quality',
                'severity': 'error',
                'message': f"Quality score below threshold: {record['quality_score']}",
                'timestamp': record['timestamp']
            })
        
        # Check error rate
        if record['error_rate'] > self.alert_thresholds.get('max_error_rate', 0.1):
            alerts.append({
                'type': 'quality',
                'severity': 'error',
                'message': f"Error rate above threshold: {record['error_rate']}",
                'timestamp': record['timestamp']
            })
        
        return alerts
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends in monitoring data."""
        if len(self.monitoring_data) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(self.monitoring_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate trends
        recent_data = df.tail(10)  # Last 10 records
        
        trends = {
            'processing_time_trend': self._calculate_trend(recent_data['processing_time']),
            'quality_score_trend': self._calculate_trend(recent_data['quality_score']),
            'error_rate_trend': self._calculate_trend(recent_data['error_rate']),
            'throughput_trend': self._calculate_trend(recent_data['records_processed'])
        }
        
        return trends
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction for a series."""
        if len(series) < 2:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        x = range(len(series))
        y = series.values
        
        # Calculate slope
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_recommendations(self, record: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on monitoring data."""
        recommendations = []
        
        if record['processing_time'] > 60:
            recommendations.append("Consider optimizing data processing for better performance")
        
        if record['quality_score'] < 0.9:
            recommendations.append("Review data quality rules and validation logic")
        
        if record['error_rate'] > 0.05:
            recommendations.append("Investigate and fix data quality issues")
        
        return recommendations
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data."""
        if not self.monitoring_data:
            return {'message': 'No monitoring data available'}
        
        # Calculate summary statistics
        df = pd.DataFrame(self.monitoring_data)
        
        summary = {
            'total_executions': len(df),
            'average_processing_time': df['processing_time'].mean(),
            'average_quality_score': df['quality_score'].mean(),
            'average_error_rate': df['error_rate'].mean(),
            'total_records_processed': df['records_processed'].sum(),
            'success_rate': len(df[df['status'] == 'success']) / len(df) * 100
        }
        
        # Get recent alerts
        recent_alerts = []
        for record in self.monitoring_data[-10:]:  # Last 10 records
            alerts = self._check_alerts(record)
            recent_alerts.extend(alerts)
        
        return {
            'summary': summary,
            'recent_alerts': recent_alerts,
            'trends': self._analyze_trends()
        }
```

### Success Metrics

#### Data Quality Metrics
- **Data Accuracy**: > 99% data accuracy
- **Data Completeness**: > 95% data completeness
- **Data Consistency**: > 98% data consistency
- **Data Timeliness**: < 5 minutes data latency

#### Performance Metrics
- **Processing Speed**: > 1000 records per minute
- **Pipeline Reliability**: > 99.9% uptime
- **Error Rate**: < 1% error rate
- **Resource Utilization**: < 80% CPU and memory usage

#### Business Impact Metrics
- **Data Availability**: > 99.5% data availability
- **User Satisfaction**: > 90% user satisfaction with data quality
- **Cost Efficiency**: > 20% reduction in data processing costs
- **Time to Insight**: < 10 minutes from data ingestion to insight

### Collaboration Patterns

#### With Lead Engineer
- Coordinate data pipeline implementation
- Ensure data processing performance
- Collaborate on data architecture decisions

#### With Back End Architect
- Design data storage and retrieval systems
- Implement data APIs and services
- Ensure data security and compliance

#### With QA Director
- Coordinate data quality testing
- Implement data validation strategies
- Ensure data testing coverage

#### With Security Engineer
- Implement data security measures
- Ensure data privacy compliance
- Coordinate data access controls
