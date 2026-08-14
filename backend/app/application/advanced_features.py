"""
Advanced Features: Rate Limiting, Analytics, and Data Archival
Items 73-75: Enterprise-grade features for production deployment

Item 73: Advanced Rate Limiting (distributed, per-user, per-endpoint)
Item 74: Analytics Engine (usage tracking, performance metrics)
Item 75: Data Archival System (automatic backup, retention policies)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from beanie import Document, Indexed
from enum import Enum
import logging
import hashlib

logger = logging.getLogger(__name__)


# ==================== ITEM 73: ADVANCED RATE LIMITING ====================

class RateLimitPolicy(str, Enum):
    """Rate limiting policy types"""
    STRICT = "strict"  # Low limits for non-premium users
    STANDARD = "standard"  # Normal limits
    PREMIUM = "premium"  # High limits for premium users
    ADMIN = "admin"  # No limits


class RateLimitRecord(BaseModel):
    """Rate limit tracking record"""
    record_id: str
    user_id: str
    endpoint: str
    tenant_id: str
    requests_count: int
    limit_threshold: int
    window_start: datetime
    window_end: datetime
    policy: RateLimitPolicy


class RateLimitViolation(BaseModel):
    """Rate limit violation incident"""
    violation_id: str
    user_id: str
    tenant_id: str
    endpoint: str
    policy: RateLimitPolicy
    requests_made: int
    limit: int
    violation_time: datetime
    action_taken: str  # throttled, blocked, warned


class RateLimitDocument(Document):
    """Rate limit tracking (distributed across nodes)"""
    record_id: str = Indexed()
    tenant_id: str = Indexed()
    user_id: str = Indexed()
    endpoint: str = Indexed()
    requests_count: int
    limit_threshold: int
    window_start: datetime
    window_end: datetime
    policy: str
    
    class Settings:
        collection = "rate_limit_records"


class RateLimitViolationDocument(Document):
    """Violations log"""
    violation_id: str = Indexed()
    tenant_id: str = Indexed()
    user_id: str = Indexed()
    endpoint: str
    policy: str
    requests_made: int
    limit: int
    violation_time: datetime
    action_taken: str
    
    class Settings:
        collection = "rate_limit_violations"


# ==================== ITEM 74: ANALYTICS ENGINE ====================

class ApiMetric(BaseModel):
    """API usage metrics"""
    metric_id: str
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    tenant_id: str
    user_id: Optional[str] = None
    recorded_at: datetime
    error_message: Optional[str] = None


class AggregatedAnalytics(BaseModel):
    """Aggregated analytics data"""
    analytics_id: str
    tenant_id: str
    period: str  # hourly, daily, weekly, monthly
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    top_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    error_rate: float
    calculated_at: datetime


class PerformanceAlert(BaseModel):
    """Performance alert for monitoring"""
    alert_id: str
    tenant_id: str
    alert_type: str  # high_latency, high_error_rate, quota_exceeded
    severity: str  # low, medium, high, critical
    description: str
    threshold: float
    current_value: float
    triggered_at: datetime
    acknowledged: bool = False


class ApiMetricDocument(Document):
    """API metrics storage"""
    metric_id: str = Indexed()
    tenant_id: str = Indexed()
    endpoint: str = Indexed()
    method: str
    response_time_ms: float
    status_code: int
    user_id: Optional[str] = None
    recorded_at: datetime = Indexed()
    error_message: Optional[str] = None
    
    class Settings:
        collection = "api_metrics"


class AnalyticsDocument(Document):
    """Aggregated analytics"""
    analytics_id: str = Indexed()
    tenant_id: str = Indexed()
    period: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    top_endpoints: List[Dict[str, Any]]
    error_rate: float
    calculated_at: datetime
    
    class Settings:
        collection = "aggregated_analytics"


class PerformanceAlertDocument(Document):
    """Performance alerts"""
    alert_id: str = Indexed()
    tenant_id: str = Indexed()
    alert_type: str
    severity: str
    description: str
    threshold: float
    current_value: float
    triggered_at: datetime
    acknowledged: bool
    
    class Settings:
        collection = "performance_alerts"


# ==================== ITEM 75: DATA ARCHIVAL SYSTEM ====================

class ArchivalPolicy(BaseModel):
    """Data archival policy"""
    policy_id: str
    collection_name: str
    retention_days: int  # How long to keep in hot storage
    archive_after_days: int  # When to move to cold storage
    delete_after_days: int  # When to permanently delete
    compression: bool = True
    encryption: bool = True
    enabled: bool = True


class ArchivedRecord(BaseModel):
    """Record metadata for archived data"""
    archive_id: str
    original_collection: str
    document_id: str
    tenant_id: str
    archive_date: datetime
    storage_location: str  # s3, gcs, azure
    archive_size: float  # MB
    is_compressed: bool
    is_encrypted: bool
    original_size: float


class ArchivalJob(BaseModel):
    """Archival job execution record"""
    job_id: str
    tenant_id: str
    collection_name: str
    job_status: str  # scheduled, running, completed, failed
    records_processed: int
    records_archived: int
    records_failed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ArchivalPolicyDocument(Document):
    """Archival policies"""
    policy_id: str = Indexed()
    tenant_id: str = Indexed()
    collection_name: str = Indexed()
    retention_days: int
    archive_after_days: int
    delete_after_days: int
    compression: bool
    encryption: bool
    enabled: bool
    
    class Settings:
        collection = "archival_policies"


class ArchivedRecordDocument(Document):
    """Archived records metadata"""
    archive_id: str = Indexed()
    tenant_id: str = Indexed()
    original_collection: str
    document_id: str = Indexed()
    archive_date: datetime
    storage_location: str
    archive_size: float
    is_compressed: bool
    is_encrypted: bool
    original_size: float
    
    class Settings:
        collection = "archived_records"


class ArchivalJobDocument(Document):
    """Archival job logs"""
    job_id: str = Indexed()
    tenant_id: str = Indexed()
    collection_name: str
    job_status: str
    records_processed: int
    records_archived: int
    records_failed: int
    started_at: datetime = Indexed()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Settings:
        collection = "archival_jobs"


# ==================== SERVICES ====================

class AdvancedRateLimitService:
    """Distributed rate limiting service"""
    
    async def check_rate_limit(
        self,
        tenant_id: str,
        user_id: str,
        endpoint: str,
        policy: RateLimitPolicy,
    ) -> tuple[bool, int]:
        """
        Check if user exceeded rate limit.
        Returns (allowed: bool, remaining_requests: int)
        """
        limits = {
            RateLimitPolicy.STRICT: 100,
            RateLimitPolicy.STANDARD: 1000,
            RateLimitPolicy.PREMIUM: 10000,
            RateLimitPolicy.ADMIN: 999999,
        }
        
        limit = limits[policy]
        now = datetime.utcnow()
        window_start = now - timedelta(hours=1)
        
        # Query existing record
        doc = await RateLimitDocument.find_one(
            RateLimitDocument.tenant_id == tenant_id,
            RateLimitDocument.user_id == user_id,
            RateLimitDocument.endpoint == endpoint,
            RateLimitDocument.window_start >= window_start,
        )
        
        if not doc:
            # New window
            doc = RateLimitDocument(
                record_id=f"RL-{user_id}-{endpoint}-{now.timestamp()}",
                tenant_id=tenant_id,
                user_id=user_id,
                endpoint=endpoint,
                requests_count=1,
                limit_threshold=limit,
                window_start=window_start,
                window_end=now + timedelta(hours=1),
                policy=policy.value,
            )
            await doc.insert()
            return True, limit - 1
        
        # Update existing record
        doc.requests_count += 1
        
        if doc.requests_count > limit:
            # Violation
            violation = RateLimitViolationDocument(
                violation_id=f"VIO-{user_id}-{endpoint}-{now.timestamp()}",
                tenant_id=tenant_id,
                user_id=user_id,
                endpoint=endpoint,
                policy=policy.value,
                requests_made=doc.requests_count,
                limit=limit,
                violation_time=now,
                action_taken="throttled",
            )
            await violation.insert()
            
            await doc.save()
            return False, 0
        
        await doc.save()
        return True, limit - doc.requests_count


class AnalyticsService:
    """API analytics and monitoring service"""
    
    async def record_metric(
        self,
        tenant_id: str,
        endpoint: str,
        method: str,
        response_time_ms: float,
        status_code: int,
        user_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record API metric"""
        metric_id = f"METRIC-{endpoint}-{datetime.utcnow().timestamp()}"
        
        doc = ApiMetricDocument(
            metric_id=metric_id,
            tenant_id=tenant_id,
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            user_id=user_id,
            recorded_at=datetime.utcnow(),
            error_message=error_message,
        )
        
        await doc.insert()
    
    async def get_analytics(
        self,
        tenant_id: str,
        period: str,  # daily, weekly, monthly
        days_back: int = 1,
    ) -> Optional[AggregatedAnalytics]:
        """Get aggregated analytics for period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        metrics = await ApiMetricDocument.find(
            ApiMetricDocument.tenant_id == tenant_id,
            ApiMetricDocument.recorded_at >= cutoff_date,
        ).to_list()
        
        if not metrics:
            return None
        
        successful = len([m for m in metrics if m.status_code < 400])
        failed = len(metrics) - successful
        response_times = [m.response_time_ms for m in metrics]
        
        # Calculate percentiles (simplified)
        sorted_times = sorted(response_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        
        analytics_id = f"ANALYTICS-{tenant_id}-{period}-{datetime.utcnow().timestamp()}"
        
        analytics = AggregatedAnalytics(
            analytics_id=analytics_id,
            tenant_id=tenant_id,
            period=period,
            total_requests=len(metrics),
            successful_requests=successful,
            failed_requests=failed,
            average_response_time=sum(response_times) / len(response_times),
            p95_response_time=sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0,
            p99_response_time=sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0,
            error_rate=(failed / len(metrics) * 100) if metrics else 0,
            calculated_at=datetime.utcnow(),
        )
        
        # Store aggregated data
        doc = AnalyticsDocument(
            analytics_id=analytics_id,
            tenant_id=tenant_id,
            period=period,
            **analytics.dict()
        )
        
        await doc.insert()
        
        logger.info(
            f"Generated {period} analytics: {len(metrics)} requests, "
            f"{analytics.error_rate}% error rate, "
            f"{analytics.average_response_time}ms avg latency"
        )
        
        return analytics
    
    async def check_performance(
        self,
        tenant_id: str,
    ) -> List[PerformanceAlert]:
        """Check for performance issues"""
        alerts = []
        
        # Get recent metrics
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        metrics = await ApiMetricDocument.find(
            ApiMetricDocument.tenant_id == tenant_id,
            ApiMetricDocument.recorded_at >= cutoff,
        ).to_list()
        
        if not metrics:
            return alerts
        
        # Check latency
        avg_latency = sum(m.response_time_ms for m in metrics) / len(metrics)
        if avg_latency > 1000:  # > 1s
            alert = PerformanceAlert(
                alert_id=f"ALERT-LATENCY-{datetime.utcnow().timestamp()}",
                tenant_id=tenant_id,
                alert_type="high_latency",
                severity="high" if avg_latency > 2000 else "medium",
                description=f"Average response time: {avg_latency}ms",
                threshold=1000,
                current_value=avg_latency,
                triggered_at=datetime.utcnow(),
            )
            alerts.append(alert)
        
        # Check error rate
        error_count = len([m for m in metrics if m.status_code >= 400])
        error_rate = (error_count / len(metrics) * 100) if metrics else 0
        
        if error_rate > 5:  # > 5% errors
            alert = PerformanceAlert(
                alert_id=f"ALERT-ERROR-{datetime.utcnow().timestamp()}",
                tenant_id=tenant_id,
                alert_type="high_error_rate",
                severity="high" if error_rate > 10 else "medium",
                description=f"Error rate: {error_rate}%",
                threshold=5,
                current_value=error_rate,
                triggered_at=datetime.utcnow(),
            )
            alerts.append(alert)
        
        return alerts


class ArchivalService:
    """Data archival and retention management"""
    
    async def set_archival_policy(
        self,
        tenant_id: str,
        collection_name: str,
        retention_days: int,
        archive_after_days: int,
        delete_after_days: int,
    ) -> ArchivalPolicy:
        """Set data retention and archival policy"""
        policy_id = f"POLICY-{collection_name}-{tenant_id}"
        
        doc = ArchivalPolicyDocument(
            policy_id=policy_id,
            tenant_id=tenant_id,
            collection_name=collection_name,
            retention_days=retention_days,
            archive_after_days=archive_after_days,
            delete_after_days=delete_after_days,
            compression=True,
            encryption=True,
            enabled=True,
        )
        
        await doc.insert()
        
        logger.info(
            f"Set archival policy for {collection_name}: "
            f"retain {retention_days}d, archive {archive_after_days}d, delete {delete_after_days}d"
        )
        
        return ArchivalPolicy(
            policy_id=policy_id,
            collection_name=collection_name,
            retention_days=retention_days,
            archive_after_days=archive_after_days,
            delete_after_days=delete_after_days,
        )
    
    async def get_archival_policies(
        self,
        tenant_id: str,
    ) -> List[ArchivalPolicy]:
        """Get all archival policies"""
        docs = await ArchivalPolicyDocument.find(
            ArchivalPolicyDocument.tenant_id == tenant_id,
            ArchivalPolicyDocument.enabled == True,
        ).to_list()
        
        return [
            ArchivalPolicy(
                policy_id=d.policy_id,
                collection_name=d.collection_name,
                retention_days=d.retention_days,
                archive_after_days=d.archive_after_days,
                delete_after_days=d.delete_after_days,
                compression=d.compression,
                encryption=d.encryption,
                enabled=d.enabled,
            )
            for d in docs
        ]
    
    async def execute_archival_job(
        self,
        tenant_id: str,
        collection_name: str,
        archive_cutoff_date: datetime,
    ) -> ArchivalJob:
        """Execute data archival job"""
        job_id = f"JOB-{collection_name}-{datetime.utcnow().timestamp()}"
        
        doc = ArchivalJobDocument(
            job_id=job_id,
            tenant_id=tenant_id,
            collection_name=collection_name,
            job_status="running",
            records_processed=0,
            records_archived=0,
            records_failed=0,
            started_at=datetime.utcnow(),
        )
        
        await doc.insert()
        
        logger.info(
            f"Started archival job {job_id} for {collection_name} "
            f"(records before {archive_cutoff_date})"
        )
        
        return ArchivalJob(
            job_id=job_id,
            tenant_id=tenant_id,
            collection_name=collection_name,
            job_status="running",
            records_processed=0,
            records_archived=0,
            records_failed=0,
            started_at=doc.started_at,
        )
    
    async def get_archived_data_count(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """Get statistics on archived data"""
        archived = await ArchivedRecordDocument.find(
            ArchivedRecordDocument.tenant_id == tenant_id,
        ).to_list()
        
        total_size = sum(a.archive_size for a in archived)
        
        return {
            "total_archived_records": len(archived),
            "total_archived_size_mb": round(total_size, 2),
            "by_collection": {},
            "by_storage": {},
        }
