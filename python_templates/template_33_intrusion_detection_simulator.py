"""
Template #33: Intrusion Detection System Simulator
Advanced security monitoring system for detecting spam and intrusion attempts
"""

import os
import json
import sqlite3
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import uuid
import csv
import io
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
import chardet

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Intrusion Detection System Simulator",
    description="Advanced security monitoring system for detecting spam and intrusion attempts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_PATH = "/workspace/intrusion_detection.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_database():
    """Initialize SQLite database for intrusion detection"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Security events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            source_ip TEXT,
            timestamp TIMESTAMP NOT NULL,
            user_agent TEXT,
            request_path TEXT,
            response_code INTEGER,
            additional_data TEXT,
            detection_rules TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Intrusion attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intrusion_attempts (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            attack_type TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            attack_vector TEXT,
            mitigation_suggestions TEXT,
            false_positive_likelihood REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES security_events (id)
        )
    ''')
    
    # Log analysis sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_sessions (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            total_lines INTEGER NOT NULL,
            processed_lines INTEGER NOT NULL,
            security_events_count INTEGER NOT NULL,
            intrusion_attempts_count INTEGER NOT NULL,
            analysis_status TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Detection patterns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_patterns (
            id TEXT PRIMARY KEY,
            pattern_name TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            regex_pattern TEXT NOT NULL,
            severity_level TEXT NOT NULL,
            description TEXT,
            false_positive_rate REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Enums for security and analysis types
class SecurityEventType(Enum):
    LOGIN_FAILURE = "login_failure"
    SUSPICIOUS_USER_AGENT = "suspicious_user_agent"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    PATH_TRAVERSAL = "path_traversal"
    RATE_LIMITING = "rate_limiting"
    UNUSUAL_ACCESS = "unusual_access"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(Enum):
    BRUTE_FORCE = "brute_force"
    USER_AGENT_SPOOFING = "user_agent_spoofing"
    AUTOMATED_ATTACK = "automated_attack"
    RECONNAISSANCE = "reconnaissance"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class LogEntry:
    """Parsed log entry structure"""
    timestamp: datetime
    source_ip: str
    user_agent: str
    request_path: str
    response_code: int
    method: str
    additional_data: Dict

@dataclass
class SecurityEvent:
    """Detected security event"""
    id: str
    event_type: SecurityEventType
    severity: SeverityLevel
    source_ip: str
    timestamp: datetime
    user_agent: str
    request_path: str
    response_code: int
    additional_data: Dict
    detection_rules: List[str]
    confidence_score: float

@dataclass
class IntrusionAttempt:
    """Identified intrusion attempt"""
    id: str
    event_id: str
    attack_type: AttackType
    confidence_score: float
    attack_vector: str
    evidence: List[str]
    mitigation_suggestions: List[str]
    false_positive_likelihood: float

class PatternRecognizer:
    """Advanced pattern recognition for security threat detection"""
    
    def __init__(self):
        self.suspicious_user_agents = self._load_suspicious_user_agents()
        self.attack_patterns = self._load_attack_patterns()
        self.geoip_data = self._load_geoip_data()
        
    def _load_suspicious_user_agents(self) -> Set[str]:
        """Load known suspicious user agent patterns"""
        return {
            # Automated tools and scanners
            "sqlmap",
            "nmap",
            "nessus",
            "openvas",
            "nikto",
            "dirb",
            "gobuster",
            "wpscan",
            "dirbuster",
            "acunetix",
            "burp",
            "zap",
            # Bot patterns
            "bot",
            "crawler",
            "spider",
            "scraper",
            # Headless browsers
            "headless",
            "phantom",
            "selenium",
            "puppeteer",
            # Generic suspicious patterns
            "python-requests",
            "curl",
            "wget",
            "java",
            "perl",
            # Empty or suspicious
            "",
            "-",
            "unknown"
        }
    
    def _load_attack_patterns(self) -> Dict[str, str]:
        """Load regex patterns for attack detection"""
        return {
            "sql_injection": r"(?i)(union\s+select|select\s+.*\s+from|drop\s+table|insert\s+into|update\s+set|delete\s+from)",
            "xss_attempt": r"(?i)(<script|javascript:|vbscript:|onload=|onerror=)",
            "path_traversal": r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%252e%252e%252f)",
            "command_injection": r"(?i)(;|\|\||&&|\$\(|\`)",
            "ldap_injection": r"(?i)(\(|\)|\||\*|\0)",
            "no_sql_injection": r"(?i)(\$where|\$ne|\$gt|\$lt)"
        }
    
    def _load_geoip_data(self) -> Dict[str, str]:
        """Load geographical IP data (simulated)"""
        return {
            # High-risk countries/regions
            "HIGH_RISK": ["CN", "RU", "KP", "IR", "SY", "YE"],
            "MEDIUM_RISK": ["BR", "IN", "VN", "TR", "MX", "AR"],
            "MONITORED": ["US", "GB", "DE", "FR", "JP", "KR"]
        }
    
    def detect_suspicious_user_agent(self, user_agent: str) -> Tuple[bool, float]:
        """Detect suspicious user agent patterns"""
        if not user_agent:
            return True, 0.9
        
        user_agent_lower = user_agent.lower()
        
        # Check against known suspicious patterns
        for suspicious_pattern in self.suspicious_user_agents:
            if suspicious_pattern in user_agent_lower:
                return True, 0.85
        
        # Check for unusual patterns
        if len(user_agent) < 10:  # Very short user agent
            return True, 0.7
        
        if user_agent.count('/') > 10:  # Too many version components
            return True, 0.6
        
        # Check for automation indicators
        automation_indicators = ["bot", "crawler", "scanner", "tool", "api"]
        if any(indicator in user_agent_lower for indicator in automation_indicators):
            return True, 0.8
        
        return False, 0.0
    
    def detect_brute_force_attempt(self, log_entries: List[LogEntry], 
                                 time_window_minutes: int = 1) -> List[SecurityEvent]:
        """Detect brute force attempts (4+ failed logins in <1 minute)"""
        brute_force_events = []
        
        # Group entries by IP address
        ip_groups = {}
        for entry in log_entries:
            if entry.source_ip not in ip_groups:
                ip_groups[entry.source_ip] = []
            ip_groups[entry.source_ip].append(entry)
        
        # Analyze each IP's activity
        for source_ip, entries in ip_groups.items():
            # Filter for failed login attempts
            failed_logins = [
                entry for entry in entries 
                if entry.response_code in [401, 403, 429]  # Failed auth codes
            ]
            
            if len(failed_logins) < 4:
                continue
            
            # Sort by timestamp
            failed_logins.sort(key=lambda x: x.timestamp)
            
            # Check for 4+ failures in time window
            for i in range(len(failed_logins) - 3):
                window_start = failed_logins[i].timestamp
                window_end = window_start + timedelta(minutes=time_window_minutes)
                
                # Count failures in this window
                window_failures = [
                    entry for entry in failed_logins[i:i+10] 
                    if window_start <= entry.timestamp <= window_end
                ]
                
                if len(window_failures) >= 4:
                    # This is a brute force attempt
                    event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        event_type=SecurityEventType.BRUTE_FORCE,
                        severity=SeverityLevel.HIGH,
                        source_ip=source_ip,
                        timestamp=window_start,
                        user_agent=window_failures[0].user_agent,
                        request_path="multiple_endpoints",
                        response_code=401,
                        additional_data={
                            "failed_attempts": len(window_failures),
                            "time_window": f"{time_window_minutes} minute(s)",
                            "affected_endpoints": list(set(entry.request_path for entry in window_failures)),
                            "first_attempt": window_failures[0].timestamp.isoformat(),
                            "last_attempt": window_failures[-1].timestamp.isoformat()
                        },
                        detection_rules=["4_failed_logins_in_window", "brute_force_pattern"],
                        confidence_score=min(0.95, 0.7 + (len(window_failures) * 0.05))
                    )
                    brute_force_events.append(event)
                    break  # Only report first occurrence per IP
        
        return brute_force_events
    
    def detect_composite_intrusion(self, log_entries: List[LogEntry]) -> List[SecurityEvent]:
        """Detect composite intrusion attempts (suspicious UA + brute force)"""
        composite_events = []
        
        # First detect suspicious user agents
        suspicious_entries = []
        for entry in log_entries:
            is_suspicious, confidence = self.detect_suspicious_user_agent(entry.user_agent)
            if is_suspicious:
                suspicious_entries.append((entry, confidence))
        
        if not suspicious_entries:
            return composite_events
        
        # Group suspicious entries by IP
        suspicious_ips = {}
        for entry, confidence in suspicious_entries:
            if entry.source_ip not in suspicious_ips:
                suspicious_ips[entry.source_ip] = []
            suspicious_ips[entry.source_ip].append((entry, confidence))
        
        # Check each suspicious IP for brute force patterns
        for source_ip, entries in suspicious_ips.items():
            entry_objects = [entry for entry, _ in entries]
            brute_force_events = self.detect_brute_force_attempt(entry_objects)
            
            for bf_event in brute_force_events:
                if bf_event.source_ip == source_ip:
                    # This is a composite intrusion
                    event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        event_type=SecurityEventType.SUSPICIOUS_USER_AGENT,
                        severity=SeverityLevel.CRITICAL,
                        source_ip=source_ip,
                        timestamp=bf_event.timestamp,
                        user_agent=bf_event.user_agent,
                        request_path=bf_event.request_path,
                        response_code=bf_event.response_code,
                        additional_data={
                            **bf_event.additional_data,
                            "composite_attack": True,
                            "suspicious_ua_confidence": max(conf for _, conf in entries),
                            "attack_classification": "automated_brute_force"
                        },
                        detection_rules=["suspicious_user_agent", "brute_force", "composite_pattern"],
                        confidence_score=min(0.98, bf_event.confidence_score + 0.1)
                    )
                    composite_events.append(event)
        
        return composite_events
    
    def detect_additional_threats(self, log_entries: List[LogEntry]) -> List[SecurityEvent]:
        """Detect additional security threats"""
        additional_events = []
        
        for entry in log_entries:
            events_from_entry = []
            
            # SQL Injection detection
            if any(pattern in entry.request_path.lower() for pattern in self.attack_patterns["sql_injection"]):
                events_from_entry.append(SecurityEvent(
                    id=str(uuid.uuid4()),
                    event_type=SecurityEventType.SQL_INJECTION,
                    severity=SeverityLevel.HIGH,
                    source_ip=entry.source_ip,
                    timestamp=entry.timestamp,
                    user_agent=entry.user_agent,
                    request_path=entry.request_path,
                    response_code=entry.response_code,
                    additional_data={"injection_pattern": "sql"},
                    detection_rules=["sql_injection_pattern"],
                    confidence_score=0.85
                ))
            
            # XSS attempt detection
            if any(pattern in entry.request_path.lower() for pattern in self.attack_patterns["xss_attempt"]):
                events_from_entry.append(SecurityEvent(
                    id=str(uuid.uuid4()),
                    event_type=SecurityEventType.XSS_ATTEMPT,
                    severity=SeverityLevel.MEDIUM,
                    source_ip=entry.source_ip,
                    timestamp=entry.timestamp,
                    user_agent=entry.user_agent,
                    request_path=entry.request_path,
                    response_code=entry.response_code,
                    additional_data={"injection_pattern": "xss"},
                    detection_rules=["xss_pattern"],
                    confidence_score=0.80
                ))
            
            # Path traversal detection
            if any(pattern in entry.request_path.lower() for pattern in self.attack_patterns["path_traversal"]):
                events_from_entry.append(SecurityEvent(
                    id=str(uuid.uuid4()),
                    event_type=SecurityEventType.PATH_TRAVERSAL,
                    severity=SeverityLevel.MEDIUM,
                    source_ip=entry.source_ip,
                    timestamp=entry.timestamp,
                    user_agent=entry.user_agent,
                    request_path=entry.request_path,
                    response_code=entry.response_code,
                    additional_data={"injection_pattern": "path_traversal"},
                    detection_rules=["path_traversal_pattern"],
                    confidence_score=0.75
                ))
            
            additional_events.extend(events_from_entry)
        
        return additional_events

class LogParser:
    """Advanced log parsing with multiple format support"""
    
    def __init__(self):
        self.supported_formats = [
            "apache_combined",
            "apache_common",
            "nginx_combined",
            "iis_w3c",
            "json_lines",
            "csv"
        ]
        
        # Regex patterns for different log formats
        self.regex_patterns = {
            "apache_combined": r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)"',
            "nginx_combined": r'(\S+) - \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)"',
            "apache_common": r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+)',
            "iis_w3c": r'(\S+) (\S+) (\S+) \[([^\]]+)\] "(\S+) (\S+)" (\d+) (\S+)',
        }
    
    def parse_log_file(self, content: bytes, filename: str) -> Tuple[List[LogEntry], str]:
        """Parse log file content and return log entries"""
        
        # Detect encoding
        detected_encoding = chardet.detect(content)['encoding'] or 'utf-8'
        
        try:
            content_str = content.decode(detected_encoding)
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            content_str = content.decode('latin-1', errors='ignore')
        
        # Detect log format
        log_format = self._detect_log_format(content_str)
        
        # Parse based on format
        if log_format == "json_lines":
            return self._parse_json_lines(content_str)
        elif log_format == "csv":
            return self._parse_csv(content_str)
        elif log_format in self.regex_patterns:
            return self._parse_regex(content_str, log_format)
        else:
            # Try common format patterns
            return self._parse_generic(content_str)
    
    def _detect_log_format(self, content: str) -> str:
        """Detect the format of the log file"""
        lines = content.split('\n')[:10]  # Check first 10 lines
        
        # Check for JSON format
        json_count = sum(1 for line in lines if line.strip().startswith('{'))
        if json_count > len(lines) * 0.5:
            return "json_lines"
        
        # Check for CSV format
        if ',' in lines[0] and 'ip' in lines[0].lower():
            return "csv"
        
        # Check for Apache/Nginx format
        for line in lines:
            if re.match(r'\S+ \S+ \S+ \[', line):
                return "apache_combined"
        
        return "generic"
    
    def _parse_json_lines(self, content: str) -> Tuple[List[LogEntry], str]:
        """Parse JSON lines format"""
        log_entries = []
        errors = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                entry = self._json_to_log_entry(data, line_num)
                if entry:
                    log_entries.append(entry)
            except json.JSONDecodeError:
                errors.append(f"Line {line_num}: Invalid JSON")
        
        return log_entries, '; '.join(errors)
    
    def _parse_csv(self, content: str) -> Tuple[List[LogEntry], str]:
        """Parse CSV format"""
        log_entries = []
        errors = []
        
        try:
            csv_reader = csv.DictReader(io.StringIO(content))
            for line_num, row in enumerate(csv_reader, 2):  # Start at line 2 (after header)
                entry = self._csv_to_log_entry(row, line_num)
                if entry:
                    log_entries.append(entry)
        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")
        
        return log_entries, '; '.join(errors)
    
    def _parse_regex(self, content: str, format_type: str) -> Tuple[List[LogEntry], str]:
        """Parse regex-based format"""
        log_entries = []
        errors = []
        pattern = self.regex_patterns[format_type]
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if not line.strip():
                continue
            
            match = re.match(pattern, line)
            if match:
                try:
                    entry = self._regex_to_log_entry(match, format_type, line_num)
                    if entry:
                        log_entries.append(entry)
                except Exception as e:
                    errors.append(f"Line {line_num}: Parsing error - {str(e)}")
            else:
                errors.append(f"Line {line_num}: Format mismatch")
        
        return log_entries, '; '.join(errors)
    
    def _parse_generic(self, content: str) -> Tuple[List[LogEntry], str]:
        """Parse generic format with flexible patterns"""
        log_entries = []
        errors = []
        
        # Try multiple generic patterns
        generic_patterns = [
            r'(\S+).*?\[([^\]]+)\].*?"(\S+) (\S+) (\S+)".*?(\d+)',  # Apache-like
            r'(\S+).*?(\d{4}-\d{2}-\d{2}).*?"(\S+) (\S+) (\S+)".*?(\d+)',  # ISO date format
        ]
        
        for pattern in generic_patterns:
            for line_num, line in enumerate(content.split('\n'), 1):
                if not line.strip():
                    continue
                
                match = re.search(pattern, line)
                if match:
                    try:
                        entry = self._generic_to_log_entry(match, line_num)
                        if entry:
                            log_entries.append(entry)
                            break  # Use first successful pattern
                    except Exception as e:
                        errors.append(f"Line {line_num}: Generic parsing error - {str(e)}")
        
        return log_entries, '; '.join(errors)
    
    def _json_to_log_entry(self, data: Dict, line_num: int) -> Optional[LogEntry]:
        """Convert JSON data to LogEntry"""
        try:
            timestamp_str = data.get('timestamp') or data.get('time') or data.get('date')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            return LogEntry(
                timestamp=timestamp,
                source_ip=data.get('ip') or data.get('source_ip') or data.get('remote_addr', '0.0.0.0'),
                user_agent=data.get('user_agent') or data.get('ua', ''),
                request_path=data.get('path') or data.get('url') or data.get('request_uri', '/'),
                response_code=int(data.get('status') or data.get('code', 200)),
                method=data.get('method') or data.get('verb', 'GET'),
                additional_data=data
            )
        except Exception:
            return None
    
    def _csv_to_log_entry(self, row: Dict, line_num: int) -> Optional[LogEntry]:
        """Convert CSV row to LogEntry"""
        try:
            timestamp_str = row.get('timestamp') or row.get('time')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            return LogEntry(
                timestamp=timestamp,
                source_ip=row.get('ip') or row.get('source_ip') or '0.0.0.0',
                user_agent=row.get('user_agent') or row.get('ua', ''),
                request_path=row.get('path') or row.get('url', '/'),
                response_code=int(row.get('status') or row.get('code', 200)),
                method=row.get('method') or 'GET',
                additional_data=dict(row)
            )
        except Exception:
            return None
    
    def _regex_to_log_entry(self, match: re.Match, format_type: str, line_num: int) -> Optional[LogEntry]:
        """Convert regex match to LogEntry"""
        try:
            groups = match.groups()
            
            if format_type in ["apache_combined", "nginx_combined"]:
                # Format: IP identity authuser [date] "method path protocol" status bytes "referer" "user_agent"
                source_ip = groups[0]
                date_str = groups[1]
                method = groups[2]
                path = groups[3]
                status = int(groups[5])
                user_agent = groups[8] if len(groups) > 8 else ''
                
                timestamp = self._parse_apache_date(date_str)
                
            elif format_type == "apache_common":
                # Format: IP identity authuser [date] "method path protocol" status bytes
                source_ip = groups[0]
                date_str = groups[1]
                method = groups[2]
                path = groups[3]
                status = int(groups[5])
                user_agent = ''
                
                timestamp = self._parse_apache_date(date_str)
            
            else:
                return None
            
            return LogEntry(
                timestamp=timestamp,
                source_ip=source_ip,
                user_agent=user_agent,
                request_path=path,
                response_code=status,
                method=method,
                additional_data={"line_number": line_num, "format": format_type}
            )
        except Exception:
            return None
    
    def _generic_to_log_entry(self, match: re.Match, line_num: int) -> Optional[LogEntry]:
        """Convert generic match to LogEntry"""
        try:
            groups = match.groups()
            source_ip = groups[0]
            date_str = groups[1]
            method = groups[2]
            path = groups[3]
            status = int(groups[4])
            
            # Try to parse date
            try:
                timestamp = datetime.fromisoformat(date_str)
            except ValueError:
                timestamp = datetime.now()
            
            return LogEntry(
                timestamp=timestamp,
                source_ip=source_ip,
                user_agent='',
                request_path=path,
                response_code=status,
                method=method,
                additional_data={"line_number": line_num, "format": "generic"}
            )
        except Exception:
            return None
    
    def _parse_apache_date(self, date_str: str) -> datetime:
        """Parse Apache date format: [01/Jan/2025:12:00:00 +0000]"""
        try:
            # Remove brackets and parse
            clean_date = date_str.strip('[]')
            # Apache format: 01/Jan/2025:12:00:00 +0000
            return datetime.strptime(clean_date, '%d/%b/%Y:%H:%M:%S %z')
        except ValueError:
            return datetime.now()

class IntrusionDetectionSystem:
    """Main intrusion detection system orchestrator"""
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.log_parser = LogParser()
        
    def analyze_log_file(self, file_content: bytes, filename: str) -> Dict:
        """Analyze log file for security threats"""
        
        # Parse log file
        log_entries, parse_errors = self.log_parser.parse_log_file(file_content, filename)
        
        if not log_entries:
            return {
                "status": "error",
                "error": "No valid log entries found",
                "parse_errors": parse_errors,
                "total_entries": 0,
                "security_events": [],
                "intrusion_attempts": []
            }
        
        # Detect security threats
        security_events = []
        
        # 1. Detect composite intrusion attempts (suspicious UA + brute force)
        composite_events = self.pattern_recognizer.detect_composite_intrusion(log_entries)
        security_events.extend(composite_events)
        
        # 2. Detect brute force attempts
        brute_force_events = self.pattern_recognizer.detect_brute_force_attempt(log_entries)
        security_events.extend(brute_force_events)
        
        # 3. Detect additional threats
        additional_events = self.pattern_recognizer.detect_additional_threats(log_entries)
        security_events.extend(additional_events)
        
        # Generate intrusion attempts from security events
        intrusion_attempts = self._generate_intrusion_attempts(security_events)
        
        # Store results in database
        session_id = self._store_analysis_session(filename, len(log_entries), security_events, intrusion_attempts)
        
        # Compile analysis results
        results = {
            "session_id": session_id,
            "status": "completed",
            "filename": filename,
            "total_entries": len(log_entries),
            "parse_errors": parse_errors,
            "security_events_count": len(security_events),
            "intrusion_attempts_count": len(intrusion_attempts),
            "security_events": [asdict(event) for event in security_events],
            "intrusion_attempts": [asdict(attempt) for attempt in intrusion_attempts],
            "analysis_summary": self._generate_analysis_summary(security_events, intrusion_attempts),
            "threat_level": self._calculate_threat_level(security_events),
            "recommendations": self._generate_recommendations(security_events, intrusion_attempts)
        }
        
        return results
    
    def _generate_intrusion_attempts(self, security_events: List[SecurityEvent]) -> List[IntrusionAttempt]:
        """Generate intrusion attempt objects from security events"""
        intrusion_attempts = []
        
        for event in security_events:
            attempt = IntrusionAttempt(
                id=str(uuid.uuid4()),
                event_id=event.id,
                attack_type=self._classify_attack_type(event),
                confidence_score=event.confidence_score,
                attack_vector=self._determine_attack_vector(event),
                evidence=self._gather_evidence(event),
                mitigation_suggestions=self._generate_mitigation_suggestions(event),
                false_positive_likelihood=self._calculate_false_positive_rate(event)
            )
            intrusion_attempts.append(attempt)
        
        return intrusion_attempts
    
    def _classify_attack_type(self, event: SecurityEvent) -> AttackType:
        """Classify the type of attack based on security event"""
        if event.event_type == SecurityEventType.BRUTE_FORCE:
            return AttackType.BRUTE_FORCE
        elif event.event_type == SecurityEventType.SUSPICIOUS_USER_AGENT:
            return AttackType.USER_AGENT_SPOOFING
        elif event.additional_data.get("composite_attack"):
            return AttackType.AUTOMATED_ATTACK
        elif event.event_type in [SecurityEventType.SQL_INJECTION, SecurityEventType.XSS_ATTEMPT]:
            return AttackType.RECONNAISSANCE
        else:
            return AttackType.UNUSUAL_ACCESS
    
    def _determine_attack_vector(self, event: SecurityEvent) -> str:
        """Determine the attack vector used"""
        if event.event_type == SecurityEventType.BRUTE_FORCE:
            return "Credential stuffing via multiple failed login attempts"
        elif event.event_type == SecurityEventType.SUSPICIOUS_USER_AGENT:
            return "Automated tool or bot using suspicious user agent"
        elif event.event_type == SecurityEventType.SQL_INJECTION:
            return "SQL injection attempt via request parameter manipulation"
        elif event.event_type == SecurityEventType.XSS_ATTEMPT:
            return "Cross-site scripting attempt via parameter injection"
        else:
            return "Suspicious request pattern requiring investigation"
    
    def _gather_evidence(self, event: SecurityEvent) -> List[str]:
        """Gather evidence for the security event"""
        evidence = []
        
        evidence.append(f"Source IP: {event.source_ip}")
        evidence.append(f"Event Type: {event.event_type.value}")
        evidence.append(f"Timestamp: {event.timestamp.isoformat()}")
        
        if event.user_agent:
            evidence.append(f"User Agent: {event.user_agent}")
        
        if event.request_path:
            evidence.append(f"Request Path: {event.request_path}")
        
        if event.response_code:
            evidence.append(f"Response Code: {event.response_code}")
        
        if event.additional_data:
            for key, value in event.additional_data.items():
                if key not in ['line_number', 'format']:
                    evidence.append(f"{key}: {value}")
        
        return evidence
    
    def _generate_mitigation_suggestions(self, event: SecurityEvent) -> List[str]:
        """Generate mitigation suggestions based on event type"""
        suggestions = []
        
        if event.event_type == SecurityEventType.BRUTE_FORCE:
            suggestions.extend([
                "Implement rate limiting for login attempts",
                "Add CAPTCHA after 3 failed attempts",
                "Consider implementing account lockout policies",
                "Monitor and block IP addresses with multiple failures",
                "Implement multi-factor authentication"
            ])
        
        elif event.event_type == SecurityEventType.SUSPICIOUS_USER_AGENT:
            suggestions.extend([
                "Block known malicious user agents",
                "Implement user agent validation",
                "Use Web Application Firewall (WAF)",
                "Monitor for automated access patterns",
                "Implement bot detection mechanisms"
            ])
        
        elif event.event_type == SecurityEventType.SQL_INJECTION:
            suggestions.extend([
                "Use parameterized queries or prepared statements",
                "Implement input validation and sanitization",
                "Deploy Web Application Firewall (WAF)",
                "Regular security code reviews",
                "Database least privilege principles"
            ])
        
        elif event.event_type == SecurityEventType.XSS_ATTEMPT:
            suggestions.extend([
                "Implement Content Security Policy (CSP)",
                "Escape user input before rendering",
                "Use output encoding for all user data",
                "Input validation for special characters",
                "Regular security testing"
            ])
        
        else:
            suggestions.extend([
                "Investigate the source IP and request patterns",
                "Review access logs for similar patterns",
                "Consider implementing additional monitoring",
                "Update security policies if needed"
            ])
        
        return suggestions
    
    def _calculate_false_positive_rate(self, event: SecurityEvent) -> float:
        """Calculate likelihood of false positive"""
        base_rate = 0.05  # 5% base false positive rate
        
        # Adjust based on event confidence
        if event.confidence_score > 0.9:
            return 0.01  # Very low false positive rate
        elif event.confidence_score > 0.8:
            return 0.02  # Low false positive rate
        elif event.confidence_score > 0.7:
            return 0.05  # Moderate false positive rate
        else:
            return 0.10  # Higher false positive rate
    
    def _generate_analysis_summary(self, security_events: List[SecurityEvent], 
                                 intrusion_attempts: List[IntrusionAttempt]) -> Dict:
        """Generate analysis summary"""
        if not security_events:
            return {
                "threat_level": "LOW",
                "total_events": 0,
                "severity_breakdown": {"low": 0, "medium": 0, "high": 0, "critical": 0},
                "event_types": {},
                "top_source_ips": [],
                "summary": "No security threats detected in the analyzed log file."
            }
        
        # Count by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for event in security_events:
            severity_counts[event.severity.value] += 1
        
        # Count by event type
        event_type_counts = {}
        for event in security_events:
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Top source IPs
        ip_counts = {}
        for event in security_events:
            ip_counts[event.source_ip] = ip_counts.get(event.source_ip, 0) + 1
        
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Overall threat level
        if severity_counts["critical"] > 0 or severity_counts["high"] > 3:
            threat_level = "CRITICAL"
        elif severity_counts["high"] > 0 or severity_counts["medium"] > 5:
            threat_level = "HIGH"
        elif severity_counts["medium"] > 0:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"
        
        return {
            "threat_level": threat_level,
            "total_events": len(security_events),
            "severity_breakdown": severity_counts,
            "event_types": event_type_counts,
            "top_source_ips": top_ips,
            "high_confidence_events": len([e for e in security_events if e.confidence_score > 0.8]),
            "summary": f"Analysis identified {len(security_events)} security events with {threat_level} threat level."
        }
    
    def _calculate_threat_level(self, security_events: List[SecurityEvent]) -> str:
        """Calculate overall threat level"""
        if not security_events:
            return "LOW"
        
        critical_count = sum(1 for e in security_events if e.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for e in security_events if e.severity == SeverityLevel.HIGH)
        medium_count = sum(1 for e in security_events if e.severity == SeverityLevel.MEDIUM)
        
        if critical_count > 0 or high_count > 3:
            return "CRITICAL"
        elif high_count > 0 or medium_count > 5:
            return "HIGH"
        elif medium_count > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, security_events: List[SecurityEvent], 
                                intrusion_attempts: List[IntrusionAttempt]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if not security_events:
            recommendations.append("No immediate security threats detected. Continue monitoring.")
            return recommendations
        
        # General recommendations based on findings
        if any(e.event_type == SecurityEventType.BRUTE_FORCE for e in security_events):
            recommendations.append("Implement rate limiting and account lockout policies to prevent brute force attacks")
        
        if any(e.event_type == SecurityEventType.SUSPICIOUS_USER_AGENT for e in security_events):
            recommendations.append("Consider implementing Web Application Firewall (WAF) rules for malicious user agents")
        
        if any(e.event_type == SecurityEventType.SQL_INJECTION for e in security_events):
            recommendations.append("Review and update input validation and parameterized queries")
        
        if any(e.event_type == SecurityEventType.XSS_ATTEMPT for e in security_events):
            recommendations.append("Implement Content Security Policy (CSP) and output encoding")
        
        # Source IP based recommendations
        ip_counts = {}
        for event in security_events:
            ip_counts[event.source_ip] = ip_counts.get(event.source_ip, 0) + 1
        
        high_activity_ips = [ip for ip, count in ip_counts.items() if count > 5]
        if high_activity_ips:
            recommendations.append(f"Consider blocking or monitoring these IPs: {', '.join(high_activity_ips)}")
        
        # Confidence-based recommendations
        high_confidence_events = [e for e in security_events if e.confidence_score > 0.9]
        if high_confidence_events:
            recommendations.append(f"Investigate {len(high_confidence_events)} high-confidence security events immediately")
        
        return recommendations
    
    def _store_analysis_session(self, filename: str, total_lines: int, 
                              security_events: List[SecurityEvent], 
                              intrusion_attempts: List[IntrusionAttempt]) -> str:
        """Store analysis session in database"""
        session_id = str(uuid.uuid4())
        
        # Calculate file hash
        # In a real implementation, you'd hash the actual file content
        file_hash = hashlib.md5(filename.encode()).hexdigest()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Store session
        cursor.execute('''
            INSERT INTO log_sessions (
                id, filename, file_hash, total_lines, processed_lines,
                security_events_count, intrusion_attempts_count, analysis_status,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            filename,
            file_hash,
            total_lines,
            total_lines,
            len(security_events),
            len(intrusion_attempts),
            "completed",
            json.dumps({
                "analysis_date": datetime.now().isoformat(),
                "detection_rules_used": ["brute_force", "suspicious_user_agent", "sql_injection", "xss_attempt"]
            })
        ))
        
        # Store security events
        for event in security_events:
            cursor.execute('''
                INSERT INTO security_events (
                    id, event_type, severity, source_ip, timestamp, user_agent,
                    request_path, response_code, additional_data, detection_rules
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id,
                event.event_type.value,
                event.severity.value,
                event.source_ip,
                event.timestamp.isoformat(),
                event.user_agent,
                event.request_path,
                event.response_code,
                json.dumps(event.additional_data),
                json.dumps(event.detection_rules)
            ))
        
        conn.commit()
        conn.close()
        
        return session_id

# Initialize intrusion detection system
ids_system = IntrusionDetectionSystem()

# API Models
class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    filename: str
    total_entries: int
    parse_errors: str
    security_events_count: int
    intrusion_attempts_count: int
    security_events: List[Dict]
    intrusion_attempts: List[Dict]
    analysis_summary: Dict
    threat_level: str
    recommendations: List[str]

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Intrusion Detection System Simulator API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze_logs": "/api/v1/analyze-logs",
            "get_session": "/api/v1/session/{session_id}",
            "security_events": "/api/v1/security-events",
            "intrusion_attempts": "/api/v1/intrusion-attempts",
            "threat_intelligence": "/api/v1/threat-intelligence",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "pattern_recognizer": "active",
            "log_parser": "ready",
            "detection_engine": "operational"
        },
        "detection_capabilities": [
            "brute_force_attacks",
            "suspicious_user_agents",
            "sql_injection",
            "xss_attempts",
            "path_traversal",
            "composite_attacks"
        ],
        "supported_formats": [
            "apache_combined",
            "nginx_combined", 
            "json_lines",
            "csv",
            "iis_w3c"
        ]
    }

@app.post("/api/v1/analyze-logs", response_model=AnalysisResponse)
async def analyze_log_file(
    log_file: UploadFile = File(..., description="Server log file to analyze"),
    analysis_type: Optional[str] = Form("comprehensive", description="Type of analysis to perform")
):
    """
    Analyze server log file for security threats and intrusion attempts
    
    - **log_file**: Server log file (supports Apache, Nginx, JSON, CSV formats)
    - **analysis_type**: Type of analysis (comprehensive, basic, threat_focused)
    
    **Detection Criteria:**
    - Non-Standard User Agent patterns
    - 4+ Failed Login Attempts in < 1 minute window
    - SQL Injection attempt patterns
    - XSS attempt patterns
    - Path traversal attempts
    """
    
    try:
        # Validate file type
        if not log_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (limit to 10MB)
        content = await log_file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Validate file type
        allowed_extensions = ['.log', '.txt', '.csv', '.json']
        if not any(log_file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Analyze the log file
        results = ids_system.analyze_log_file(content, log_file.filename)
        
        return JSONResponse(content=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/session/{session_id}")
async def get_analysis_session(session_id: str):
    """Get previously completed analysis session"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT filename, file_hash, total_lines, processed_lines,
                   security_events_count, intrusion_attempts_count, analysis_status,
                   started_at, completed_at, metadata
            FROM log_sessions WHERE id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Analysis session not found")
        
        (
            filename, file_hash, total_lines, processed_lines,
            security_events_count, intrusion_attempts_count, analysis_status,
            started_at, completed_at, metadata_json
        ) = result
        
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Get security events for this session
        cursor.execute('''
            SELECT id, event_type, severity, source_ip, timestamp, user_agent,
                   request_path, response_code, additional_data, detection_rules
            FROM security_events 
            WHERE id IN (
                SELECT event_id FROM intrusion_attempts WHERE session_id = ?
            )
        ''', (session_id,))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "id": row[0],
                "event_type": row[1],
                "severity": row[2],
                "source_ip": row[3],
                "timestamp": row[4],
                "user_agent": row[5],
                "request_path": row[6],
                "response_code": row[7],
                "additional_data": json.loads(row[8]),
                "detection_rules": json.loads(row[9])
            })
        
        conn.close()
        
        return {
            "session_id": session_id,
            "filename": filename,
            "total_lines": total_lines,
            "processed_lines": processed_lines,
            "security_events_count": security_events_count,
            "intrusion_attempts_count": intrusion_attempts_count,
            "analysis_status": analysis_status,
            "started_at": started_at,
            "completed_at": completed_at,
            "security_events": events,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@app.get("/api/v1/security-events")
async def list_security_events(limit: int = 50, severity: Optional[str] = None):
    """List recent security events"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, event_type, severity, source_ip, timestamp, user_agent,
                   request_path, response_code, additional_data, detection_rules
            FROM security_events
        '''
        params = []
        
        if severity:
            query += ' WHERE severity = ?'
            params.append(severity)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "id": row[0],
                "event_type": row[1],
                "severity": row[2],
                "source_ip": row[3],
                "timestamp": row[4],
                "user_agent": row[5],
                "request_path": row[6],
                "response_code": row[7],
                "additional_data": json.loads(row[8]),
                "detection_rules": json.loads(row[9])
            })
        
        conn.close()
        
        return {
            "events": events,
            "total": len(events),
            "filters_applied": {"severity": severity} if severity else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list security events: {str(e)}")

@app.get("/api/v1/intrusion-attempts")
async def list_intrusion_attempts(limit: int = 50, attack_type: Optional[str] = None):
    """List recent intrusion attempts"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, event_id, attack_type, confidence_score, attack_vector,
                   mitigation_suggestions, false_positive_likelihood, created_at
            FROM intrusion_attempts
        '''
        params = []
        
        if attack_type:
            query += ' WHERE attack_type = ?'
            params.append(attack_type)
        
        query += ' ORDER BY confidence_score DESC, created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        attempts = []
        for row in cursor.fetchall():
            attempts.append({
                "id": row[0],
                "event_id": row[1],
                "attack_type": row[2],
                "confidence_score": row[3],
                "attack_vector": row[4],
                "mitigation_suggestions": json.loads(row[5]),
                "false_positive_likelihood": row[6],
                "created_at": row[7]
            })
        
        conn.close()
        
        return {
            "intrusion_attempts": attempts,
            "total": len(attempts),
            "filters_applied": {"attack_type": attack_type} if attack_type else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list intrusion attempts: {str(e)}")

@app.get("/api/v1/threat-intelligence")
async def get_threat_intelligence():
    """Get threat intelligence and system statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get overall statistics
        cursor.execute('SELECT COUNT(*) FROM security_events')
        total_events = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM intrusion_attempts')
        total_attempts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM log_sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Get severity breakdown
        cursor.execute('''
            SELECT severity, COUNT(*) 
            FROM security_events 
            GROUP BY severity
        ''')
        severity_breakdown = dict(cursor.fetchall())
        
        # Get event type breakdown
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM security_events 
            GROUP BY event_type
        ''')
        event_type_breakdown = dict(cursor.fetchall())
        
        # Get top source IPs
        cursor.execute('''
            SELECT source_ip, COUNT(*) as event_count
            FROM security_events 
            GROUP BY source_ip 
            ORDER BY event_count DESC 
            LIMIT 10
        ''')
        top_ips = [{"ip": row[0], "events": row[1]} for row in cursor.fetchall()]
        
        # Get recent high-confidence events
        cursor.execute('''
            SELECT id, event_type, severity, source_ip, timestamp, confidence_score
            FROM security_events 
            WHERE confidence_score > 0.8
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        high_confidence_events = [
            {
                "id": row[0],
                "event_type": row[1],
                "severity": row[2],
                "source_ip": row[3],
                "timestamp": row[4],
                "confidence_score": row[5]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "overview": {
                "total_security_events": total_events,
                "total_intrusion_attempts": total_attempts,
                "total_analysis_sessions": total_sessions
            },
            "severity_breakdown": severity_breakdown,
            "event_type_breakdown": event_type_breakdown,
            "top_source_ips": top_ips,
            "high_confidence_events": high_confidence_events,
            "system_health": "operational",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat intelligence: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)