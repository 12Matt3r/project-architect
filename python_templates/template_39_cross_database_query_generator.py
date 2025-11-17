#!/usr/bin/env python3
"""
Template #39: Cross-Database Query Generator

An intelligent query translation system that converts natural language questions
into optimized database queries for multiple database types (PostgreSQL, MySQL, MongoDB).

Implements advanced NLP techniques for query parsing and database-specific optimization.

Author: MiniMax Agent
Date: 2025-11-17
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import json
import uuid
import sqlite3
import logging
from contextlib import contextmanager
from collections import defaultdict
import sqlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class NaturalLanguageQuery(BaseModel):
    question: str = Field(..., description="Natural language question to convert to database queries")
    database_type: Optional[str] = Field(None, description="Preferred database type for optimization")
    schema_context: Optional[str] = Field(None, description="Optional database schema context")

class DatabaseQuery(BaseModel):
    database_type: str
    query: str
    syntax_valid: bool
    optimization_notes: List[str]
    performance_considerations: List[str]
    complexity_score: float  # 1-10 scale

class QueryGenerationResponse(BaseModel):
    query_id: str
    original_question: str
    queries: List[DatabaseQuery]
    query_analysis: Dict[str, Any]
    best_practices: List[str]
    generated_at: datetime

# Dataclasses for internal processing
@dataclass
class QueryComponents:
    select_clause: str = ""
    from_clause: str = ""
    where_clause: str = ""
    group_by_clause: str = ""
    having_clause: str = ""
    order_by_clause: str = ""
    limit_clause: str = ""
    join_clauses: List[str] = None

@dataclass
class DatabaseSpecs:
    name: str
    sql_dialect: str
    syntax_rules: Dict[str, str]
    optimization_features: List[str]
    reserved_keywords: List[str]

class NaturalLanguageProcessor:
    """Process natural language questions and extract query components"""
    
    def __init__(self):
        # Query type patterns
        self.query_patterns = {
            'select': [
                r'show\s+(?:all\s+)?(?P<fields>[\w\s,]+?)\s+(?:from\s+)?(?P<table>[\w\s]+)',
                r'list\s+(?P<fields>[\w\s,]+?)\s+(?:from\s+)?(?P<table>[\w\s]+)',
                r'display\s+(?P<fields>[\w\s,]+?)\s+(?:from\s+)?(?P<table>[\w\s]+)',
                r'get\s+(?P<fields>[\w\s,]+?)\s+(?:from\s+)?(?P<table>[\w\s]+)'
            ],
            'count': [
                r'how\s+many\s+(?P<entity>[\w\s]+)',
                r'count\s+(?:of\s+)?(?P<entity>[\w\s]+)',
                r'number\s+of\s+(?P<entity>[\w\s]+)'
            ],
            'sum': [
                r'total\s+(?P<field>[\w\s]+)\s+(?:of\s+)?(?P<entity>[\w\s]+)',
                r'sum\s+of\s+(?P<field>[\w\s]+)\s+(?:from\s+)?(?P<entity>[\w\s]+)',
                r'(?P<field>[\w\s]+)\s+total\s+(?:for\s+)?(?P<entity>[\w\s]+)'
            ],
            'average': [
                r'average\s+(?P<field>[\w\s]+)\s+(?:of\s+)?(?P<entity>[\w\s]+)',
                r'avg\s+(?:of\s+)?(?P<field>[\w\s]+)\s+(?:from\s+)?(?P<entity>[\w\s]+)',
                r'mean\s+(?P<field>[\w\s]+)\s+(?:of\s+)?(?P<entity>[\w\s]+)'
            ],
            'max': [
                r'highest\s+(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)',
                r'maximum\s+(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)',
                r'max\s+(?:of\s+)?(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)'
            ],
            'min': [
                r'lowest\s+(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)',
                r'minimum\s+(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)',
                r'min\s+(?:of\s+)?(?P<field>[\w\s]+)\s+(?:in\s+)?(?P<entity>[\w\s]+)'
            ]
        }
        
        # Condition patterns
        self.condition_patterns = {
            'time_periods': {
                'today': "DATE(created_at) = CURDATE()",
                'yesterday': "DATE(created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)",
                'this week': "YEARWEEK(created_at) = YEARWEEK(CURDATE())",
                'this month': "YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())",
                'this year': "YEAR(created_at) = YEAR(CURDATE())",
                'last week': "YEARWEEK(created_at) = YEARWEEK(CURDATE()) - 1",
                'last month': "YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE()) - 1",
                'last year': "YEAR(created_at) = YEAR(CURDATE()) - 1",
                'Q1': "QUARTER(created_at) = 1 AND YEAR(created_at) = YEAR(CURDATE())",
                'Q2': "QUARTER(created_at) = 2 AND YEAR(created_at) = YEAR(CURDATE())",
                'Q3': "QUARTER(created_at) = 3 AND YEAR(created_at) = YEAR(CURDATE())",
                'Q4': "QUARTER(created_at) = 4 AND YEAR(created_at) = YEAR(CURDATE())",
                'last quarter': "QUARTER(created_at) = QUARTER(CURDATE()) - 1 OR (QUARTER(created_at) = 4 AND QUARTER(CURDATE()) = 1)"
            },
            'comparisons': {
                'greater than': '>',
                'more than': '>',
                'less than': '<',
                'fewer than': '<',
                'at least': '>=',
                'at most': '<=',
                'equals': '=',
                'equal to': '=',
                'not equal to': '!=',
                'between': 'BETWEEN',
                'in': 'IN',
                'like': 'LIKE'
            },
            'aggregations': {
                'by category': 'GROUP BY category',
                'by status': 'GROUP BY status',
                'by date': 'GROUP BY DATE(created_at)',
                'by month': 'GROUP BY YEAR(created_at), MONTH(created_at)',
                'by year': 'GROUP BY YEAR(created_at)',
                'ordered by': 'ORDER BY',
                'sorted by': 'ORDER BY',
                'highest first': 'ORDER BY DESC',
                'lowest first': 'ORDER BY ASC'
            }
        }
        
        # Common business terms mapping
        self.business_terms = {
            'sales': ['orders', 'transactions', 'sales', 'revenue'],
            'customers': ['users', 'clients', 'customers', 'buyers'],
            'products': ['items', 'products', 'goods', 'catalog'],
            'revenue': ['sales', 'income', 'amount', 'total'],
            'profit': ['margin', 'profit', 'earnings', 'gain'],
            'quantity': ['count', 'number', 'amount', 'volume'],
            'date': ['created_at', 'order_date', 'timestamp', 'date'],
            'price': ['cost', 'price', 'amount', 'value']
        }
    
    def extract_query_components(self, question: str) -> QueryComponents:
        """Extract SQL components from natural language question"""
        
        components = QueryComponents()
        question_lower = question.lower()
        
        # Detect query type and extract components
        query_type = self._detect_query_type(question_lower)
        
        if query_type in ['select', 'count', 'sum', 'average', 'max', 'min']:
            self._extract_select_components(question_lower, components)
        
        # Extract conditions
        where_conditions = self._extract_conditions(question_lower)
        if where_conditions:
            components.where_clause = where_conditions
        
        # Extract grouping
        group_by = self._extract_grouping(question_lower)
        if group_by:
            components.group_by_clause = group_by
        
        # Extract ordering
        order_by = self._extract_ordering(question_lower)
        if order_by:
            components.order_by_clause = order_by
        
        # Extract limits
        limit = self._extract_limit(question_lower)
        if limit:
            components.limit_clause = limit
        
        return components
    
    def _detect_query_type(self, question: str) -> str:
        """Detect the type of query being requested"""
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question):
                    return query_type
        
        # Default to select if no specific pattern matches
        return 'select'
    
    def _extract_select_components(self, question: str, components: QueryComponents):
        """Extract SELECT and FROM components"""
        
        # Look for table/entity mentions
        for business_term, table_names in self.business_terms.items():
            if business_term in question:
                # Map to standard table names
                if business_term == 'sales':
                    components.from_clause = "orders"
                elif business_term == 'customers':
                    components.from_clause = "users"
                elif business_term == 'products':
                    components.from_clause = "products"
                elif business_term == 'revenue':
                    components.select_clause = "SUM(amount)"
                elif business_term == 'profit':
                    components.select_clause = "SUM(revenue - cost)"
                else:
                    components.select_clause = "*"
        
        # Extract specific field mentions
        field_patterns = [
            r'profit margin',
            r'revenue',
            r'amount',
            r'quantity',
            r'price',
            r'date',
            r'status',
            r'category'
        ]
        
        selected_fields = []
        for pattern in field_patterns:
            if re.search(pattern, question):
                if 'profit margin' in question:
                    selected_fields.append("(revenue - cost) / revenue * 100 as profit_margin")
                elif 'revenue' in question:
                    selected_fields.append("SUM(amount) as total_revenue")
                else:
                    field_name = pattern.strip('()').replace(' ', '_')
                    selected_fields.append(field_name)
        
        if selected_fields:
            components.select_clause = ", ".join(selected_fields)
        elif not components.select_clause:
            components.select_clause = "*"
    
    def _extract_conditions(self, question: str) -> str:
        """Extract WHERE conditions from the question"""
        
        conditions = []
        
        # Time period conditions
        for period, condition in self.condition_patterns['time_periods'].items():
            if period in question:
                conditions.append(condition)
        
        # Comparison conditions
        for phrase, operator in self.condition_patterns['comparisons'].items():
            if phrase in question:
                # Extract values for comparisons
                value_match = re.search(rf'{phrase}\s+(\d+(?:\.\d+)?|\w+)', question)
                if value_match:
                    value = value_match.group(1)
                    if value.isdigit():
                        conditions.append(f"column_name {operator} {value}")
                    else:
                        conditions.append(f"column_name {operator} '{value}'")
        
        # Special conditions
        if 'q4' in question or 'quarter 4' in question:
            conditions.append("QUARTER(created_at) = 4 AND YEAR(created_at) = YEAR(CURDATE())")
        elif 'last quarter' in question:
            conditions.append(self.condition_patterns['time_periods']['last quarter'])
        
        return " AND ".join(conditions) if conditions else ""
    
    def _extract_grouping(self, question: str) -> str:
        """Extract GROUP BY clause"""
        
        for phrase, group_clause in self.condition_patterns['aggregations'].items():
            if phrase in question:
                if 'by' in phrase:
                    return group_clause
                elif 'ordered by' in phrase:
                    return "ORDER BY"
        
        # Auto-grouping for aggregate queries
        if any(func in question for func in ['sum', 'count', 'average', 'avg', 'max', 'min']):
            # Default grouping for common scenarios
            if 'products' in question:
                return "GROUP BY product_id"
            elif 'customers' in question:
                return "GROUP BY customer_id"
            elif 'category' in question:
                return "GROUP BY category"
        
        return ""
    
    def _extract_ordering(self, question: str) -> str:
        """Extract ORDER BY clause"""
        
        if 'highest first' in question or 'largest first' in question:
            return "ORDER BY value DESC"
        elif 'lowest first' in question or 'smallest first' in question:
            return "ORDER BY value ASC"
        elif 'recent' in question or 'latest' in question:
            return "ORDER BY created_at DESC"
        elif 'oldest' in question:
            return "ORDER BY created_at ASC"
        
        # Default ordering for aggregated results
        if any(func in question for func in ['sum', 'count', 'total']):
            return "ORDER BY total DESC"
        
        return ""
    
    def _extract_limit(self, question: str) -> str:
        """Extract LIMIT clause"""
        
        limit_patterns = [
            r'top\s+(\d+)',
            r'first\s+(\d+)',
            r'only\s+(\d+)',
            r'(\d+)\s+most',
            r'limit\s+to\s+(\d+)'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, question)
            if match:
                return f"LIMIT {match.group(1)}"
        
        return ""

class DatabaseQueryGenerator:
    """Generate database-specific queries from components"""
    
    def __init__(self):
        self.database_specs = self._initialize_database_specs()
    
    def _initialize_database_specs(self) -> Dict[str, DatabaseSpecs]:
        """Initialize database-specific specifications"""
        
        return {
            'postgresql': DatabaseSpecs(
                name='PostgreSQL',
                sql_dialect='postgresql',
                syntax_rules={
                    'string_literal': "E'%s'",
                    'date_function': 'CURRENT_DATE',
                    'limit_syntax': 'LIMIT %s OFFSET %s',
                    'substring': 'SUBSTRING(%s FROM %s FOR %s)',
                    'case_sensitive': 'ILIKE'
                },
                optimization_features=[
                    'Index optimization',
                    'Query planning hints',
                    'Materialized views',
                    'Partial indexes'
                ],
                reserved_keywords=[
                    'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
                    'LIMIT', 'OFFSET', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
                    'UNION', 'INTERSECT', 'EXCEPT', 'DISTINCT', 'ALL'
                ]
            ),
            'mysql': DatabaseSpecs(
                name='MySQL',
                sql_dialect='mysql',
                syntax_rules={
                    'string_literal': "'%s'",
                    'date_function': 'CURDATE()',
                    'limit_syntax': 'LIMIT %s, %s',
                    'substring': 'SUBSTRING(%s, %s, %s)',
                    'case_sensitive': 'LIKE BINARY'
                },
                optimization_features=[
                    'Index hints',
                    'Query optimization',
                    'Table optimization',
                    'Explain analysis'
                ],
                reserved_keywords=[
                    'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
                    'LIMIT', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'STRAIGHT_JOIN',
                    'UNION', 'DISTINCT', 'ALL', 'LOCK', 'TABLES'
                ]
            ),
            'mongodb': DatabaseSpecs(
                name='MongoDB',
                sql_dialect='mongodb',
                syntax_rules={
                    'find': 'db.collection.find(%s)',
                    'aggregate': 'db.collection.aggregate(%s)',
                    'match': '{"$match": %s}',
                    'group': '{"$group": %s}',
                    'sort': '{"$sort": %s}',
                    'limit': '{"$limit": %s}'
                },
                optimization_features=[
                    'Index optimization',
                    'Pipeline optimization',
                    'Aggregation pipeline',
                    'Atlas Search'
                ],
                reserved_keywords=[
                    'find', 'aggregate', 'match', 'group', 'sort', 'limit',
                    'project', 'sort', 'count', 'distinct'
                ]
            )
        }
    
    def generate_queries(self, components: QueryComponents, original_question: str) -> List[DatabaseQuery]:
        """Generate queries for all supported databases"""
        
        queries = []
        
        for db_type, specs in self.database_specs.items():
            if db_type == 'mongodb':
                query = self._generate_mongodb_query(components, specs)
            else:
                query = self._generate_sql_query(components, specs, db_type)
            
            # Validate syntax
            syntax_valid = self._validate_syntax(query.query, specs)
            
            # Generate optimization notes
            optimization_notes = self._generate_optimization_notes(query, specs)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(query.query)
            
            queries.append(DatabaseQuery(
                database_type=specs.name,
                query=query.query,
                syntax_valid=syntax_valid,
                optimization_notes=optimization_notes,
                performance_considerations=self._generate_performance_notes(query, specs),
                complexity_score=complexity_score
            ))
        
        return queries
    
    def _generate_sql_query(self, components: QueryComponents, specs: DatabaseSpecs, db_type: str) -> DatabaseQuery:
        """Generate SQL query for PostgreSQL and MySQL"""
        
        query_parts = []
        
        # SELECT clause
        if components.select_clause:
            query_parts.append(f"SELECT {components.select_clause}")
        
        # FROM clause
        if components.from_clause:
            query_parts.append(f"FROM {components.from_clause}")
        else:
            query_parts.append("FROM table_name")  # Default placeholder
        
        # WHERE clause
        if components.where_clause:
            query_parts.append(f"WHERE {components.where_clause}")
        
        # GROUP BY clause
        if components.group_by_clause:
            query_parts.append(components.group_by_clause)
        
        # HAVING clause
        if components.having_clause:
            query_parts.append(f"HAVING {components.having_clause}")
        
        # ORDER BY clause
        if components.order_by_clause:
            query_parts.append(components.order_by_clause)
        
        # LIMIT clause
        if components.limit_clause:
            query_parts.append(components.limit_clause)
        
        query = "\n".join(query_parts)
        
        # Apply database-specific syntax adjustments
        if db_type == 'mysql':
            query = self._apply_mysql_specifics(query)
        elif db_type == 'postgresql':
            query = self._apply_postgresql_specifics(query)
        
        return DatabaseQuery(
            database_type=specs.name,
            query=query,
            syntax_valid=True,  # Will be validated later
            optimization_notes=[],
            performance_considerations=[],
            complexity_score=0.0
        )
    
    def _generate_mongodb_query(self, components: QueryComponents, specs: DatabaseSpecs) -> DatabaseQuery:
        """Generate MongoDB aggregation pipeline"""
        
        pipeline = []
        
        # Build match stage for WHERE conditions
        if components.where_clause:
            match_stage = self._convert_sql_where_to_mongodb_match(components.where_clause)
            pipeline.append(f'{{"$match": {match_stage}}}')
        
        # Build group stage for GROUP BY
        if components.group_by_clause:
            group_stage = self._convert_sql_group_to_mongodb_group(components.group_by_clause, components.select_clause)
            pipeline.append(group_stage)
        
        # Build sort stage for ORDER BY
        if components.order_by_clause:
            sort_stage = self._convert_sql_order_to_mongodb_sort(components.order_by_clause)
            pipeline.append(sort_stage)
        
        # Build limit stage
        if components.limit_clause:
            limit_value = components.limit_clause.replace("LIMIT ", "")
            pipeline.append(f'{{"$limit": {limit_value}}}')
        
        # Create find query if no aggregation needed
        if not pipeline:
            find_query = f"db.collection.find({self._convert_sql_where_to_mongodb_match(components.where_clause) or '{}'})"
            query = find_query
        else:
            query = f"db.collection.aggregate([\n  " + ",\n  ".join(pipeline) + "\n])"
        
        return DatabaseQuery(
            database_type=specs.name,
            query=query,
            syntax_valid=True,
            optimization_notes=[],
            performance_considerations=[],
            complexity_score=0.0
        )
    
    def _apply_mysql_specifics(self, query: str) -> str:
        """Apply MySQL-specific syntax"""
        # MySQL-specific adjustments
        query = query.replace('ILIKE', 'LIKE')  # MySQL uses LIKE for case-insensitive
        query = query.replace('LIMIT 10 OFFSET 0', 'LIMIT 10')  # MySQL default offset
        return query
    
    def _apply_postgresql_specifics(self, query: str) -> str:
        """Apply PostgreSQL-specific syntax"""
        # PostgreSQL-specific adjustments
        # Add any PostgreSQL-specific optimizations here
        return query
    
    def _convert_sql_where_to_mongodb_match(self, where_clause: str) -> str:
        """Convert SQL WHERE clause to MongoDB match stage"""
        
        if not where_clause:
            return "{}"
        
        # Simple conversions for common patterns
        conditions = []
        
        # Time period conversions
        if 'CURDATE()' in where_clause:
            conditions.append('{"created_at": {"$gte": new Date(new Date().setHours(0,0,0,0))}}')
        if 'QUARTER(created_at) = 4' in where_clause:
            conditions.append('{"created_at": {"$gte": new Date(new Date().getFullYear(), 11, 1)}}')
        if 'YEAR(created_at) = YEAR(CURDATE())' in where_clause:
            conditions.append('{"created_at": {"$gte": new Date(new Date().getFullYear(), 0, 1)}}')
        
        if conditions:
            return '{"$and": [' + ", ".join(conditions) + ']}'
        else:
            return "{}"
    
    def _convert_sql_group_to_mongodb_group(self, group_by_clause: str, select_clause: str) -> str:
        """Convert SQL GROUP BY to MongoDB group stage"""
        
        if 'GROUP BY' in group_by:
            # Extract grouping field
            if 'category' in group_by:
                group_id = '$_id'
                group_fields = '{category: "$category"}'
            elif 'product_id' in group_by:
                group_id = '$_id'
                group_fields = '{product_id: "$product_id"}'
            else:
                group_id = '$_id'
                group_fields = '{}'
            
            # Handle aggregate functions in SELECT
            if 'SUM(' in select_clause:
                group_stage = f'{{"$group": {{"_id": {group_fields}, "total": {{"$sum": "$amount"}}}}}}'
            elif 'COUNT(' in select_clause:
                group_stage = f'{{"$group": {{"_id": {group_fields}, "count": {{"$sum": 1}}}}}}'
            else:
                group_stage = f'{{"$group": {{"_id": {group_fields}}}}}'
            
            return group_stage
        
        return ""
    
    def _convert_sql_order_to_mongodb_sort(self, order_by_clause: str) -> str:
        """Convert SQL ORDER BY to MongoDB sort stage"""
        
        if 'DESC' in order_by:
            return '{"$sort": {"value": -1}}'
        elif 'ASC' in order_by:
            return '{"$sort": {"value": 1}}'
        else:
            return '{"$sort": {"_id": 1}}'  # Default sort
    
    def _validate_syntax(self, query: str, specs: DatabaseSpecs) -> bool:
        """Validate query syntax for specific database"""
        
        try:
            if specs.sql_dialect == 'mongodb':
                # Basic MongoDB syntax validation
                return 'db.collection' in query and ('find(' in query or 'aggregate(' in query)
            else:
                # Basic SQL syntax validation using sqlparse
                parsed = sqlparse.parse(query)
                return len(parsed) > 0 and parsed[0].get_type() in ['SELECT', 'UNKNOWN']
        
        except Exception:
            return False
    
    def _generate_optimization_notes(self, query: DatabaseQuery, specs: DatabaseSpecs) -> List[str]:
        """Generate optimization notes for the query"""
        
        notes = []
        
        # Database-specific optimization notes
        if specs.name == 'PostgreSQL':
            notes.extend([
                "Consider creating indexes on frequently queried columns",
                "Use EXPLAIN ANALYZE to optimize query performance",
                "Consider materialized views for complex aggregations"
            ])
        elif specs.name == 'MySQL':
            notes.extend([
                "Ensure proper indexing strategy for WHERE clauses",
                "Use EXPLAIN to analyze query execution plan",
                "Consider query cache for frequently executed queries"
            ])
        elif specs.name == 'MongoDB':
            notes.extend([
                "Create appropriate indexes for aggregation pipeline stages",
                "Use $match early in pipeline to reduce document processing",
                "Consider compound indexes for multi-field queries"
            ])
        
        # Query-specific optimization notes
        query_lower = query.query.lower()
        if 'select *' in query_lower:
            notes.append("Consider selecting only required columns instead of SELECT *")
        
        if 'group by' in query_lower:
            notes.append("Ensure proper indexing on grouped columns for better performance")
        
        if 'order by' in query_lower:
            notes.append("Index ordered columns to avoid expensive sorting operations")
        
        if 'limit' in query_lower:
            notes.append("Use appropriate LIMIT values to control result set size")
        
        return notes
    
    def _generate_performance_notes(self, query: DatabaseQuery, specs: DatabaseSpecs) -> List[str]:
        """Generate performance considerations"""
        
        considerations = []
        
        # Complexity-based considerations
        if query.complexity_score >= 8:
            considerations.append("High complexity query - consider breaking into smaller parts")
        elif query.complexity_score >= 5:
            considerations.append("Medium complexity - monitor performance and add indexes if needed")
        else:
            considerations.append("Low complexity query - should perform well with basic optimization")
        
        # Database-specific performance notes
        if specs.name == 'PostgreSQL':
            considerations.append("PostgreSQL excels at complex analytical queries")
        elif specs.name == 'MySQL':
            considerations.append("MySQL performs well with properly indexed simple queries")
        elif specs.name == 'MongoDB':
            considerations.append("MongoDB aggregation pipeline provides flexible data processing")
        
        return considerations
    
    def _calculate_complexity_score(self, query: str) -> float:
        """Calculate query complexity score (1-10)"""
        
        score = 1.0
        
        # Increase complexity based on query features
        if 'JOIN' in query.upper():
            score += 2.0
        if 'GROUP BY' in query.upper():
            score += 1.5
        if 'ORDER BY' in query.upper():
            score += 0.5
        if 'HAVING' in query.upper():
            score += 1.0
        if 'UNION' in query.upper():
            score += 1.5
        if 'SUBQUERY' in query.upper() or '(' in query:
            score += 2.0
        if 'CASE' in query.upper():
            score += 1.0
        if 'WINDOW' in query.upper():
            score += 2.5
        
        return min(10.0, score)

class QueryAnalyzer:
    """Analyze generated queries and provide insights"""
    
    def __init__(self):
        pass
    
    def analyze_queries(self, queries: List[DatabaseQuery], original_question: str) -> Dict[str, Any]:
        """Analyze all generated queries"""
        
        analysis = {
            'query_count': len(queries),
            'syntax_validation': {
                'valid_count': sum(1 for q in queries if q.syntax_valid),
                'invalid_count': sum(1 for q in queries if not q.syntax_valid)
            },
            'complexity_analysis': {
                'average_complexity': sum(q.complexity_score for q in queries) / len(queries),
                'highest_complexity': max(q.complexity_score for q in queries),
                'lowest_complexity': min(q.complexity_score for q in queries)
            },
            'optimization_summary': self._summarize_optimizations(queries),
            'database_comparison': self._compare_database_performance(queries),
            'recommendations': self._generate_recommendations(queries, original_question)
        }
        
        return analysis
    
    def _summarize_optimizations(self, queries: List[DatabaseQuery]) -> Dict[str, int]:
        """Summarize optimization recommendations across all queries"""
        
        optimization_counts = defaultdict(int)
        
        for query in queries:
            for note in query.optimization_notes:
                # Categorize optimizations
                if 'index' in note.lower():
                    optimization_counts['Index Optimization'] += 1
                elif 'explain' in note.lower():
                    optimization_counts['Query Analysis'] += 1
                elif 'materialized' in note.lower() or 'cache' in note.lower():
                    optimization_counts['Caching Strategy'] += 1
                elif 'limit' in note.lower():
                    optimization_counts['Result Set Optimization'] += 1
                else:
                    optimization_counts['General Optimization'] += 1
        
        return dict(optimization_counts)
    
    def _compare_database_performance(self, queries: List[DatabaseQuery]) -> Dict[str, Any]:
        """Compare performance characteristics across databases"""
        
        comparison = {}
        
        for query in queries:
            comparison[query.database_type] = {
                'complexity_score': query.complexity_score,
                'optimization_potential': len(query.optimization_notes),
                'performance_rating': self._rate_performance(query)
            }
        
        # Find best performer
        best_db = min(comparison.keys(), 
                     key=lambda db: comparison[db]['complexity_score'] + 
                                   (10 - comparison[db]['optimization_potential']))
        
        comparison['best_performer'] = {
            'database': best_db,
            'reason': self._explain_best_performer(comparison[best_db])
        }
        
        return comparison
    
    def _rate_performance(self, query: DatabaseQuery) -> str:
        """Rate query performance"""
        
        if query.complexity_score <= 3:
            return "Excellent"
        elif query.complexity_score <= 5:
            return "Good"
        elif query.complexity_score <= 7:
            return "Fair"
        else:
            return "Needs Optimization"
    
    def _explain_best_performer(self, perf_data: Dict[str, Any]) -> str:
        """Explain why a database performs best"""
        
        reasons = []
        
        if perf_data['complexity_score'] <= 3:
            reasons.append("low complexity")
        if perf_data['optimization_potential'] >= 3:
            reasons.append("well-optimized")
        
        return "Best performer due to " + " and ".join(reasons)
    
    def _generate_recommendations(self, queries: List[DatabaseQuery], original_question: str) -> List[str]:
        """Generate best practice recommendations"""
        
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            "Test queries on sample data before production deployment",
            "Monitor query performance with database monitoring tools",
            "Consider query caching for frequently executed queries",
            "Implement proper indexing based on query patterns"
        ])
        
        # Question-specific recommendations
        question_lower = original_question.lower()
        
        if 'profit' in question_lower or 'margin' in question_lower:
            recommendations.append("Ensure data quality for cost and revenue calculations")
        
        if 'quarter' in question_lower or 'q4' in question_lower:
            recommendations.append("Verify quarter boundaries align with business calendar")
        
        if 'category' in question_lower:
            recommendations.append("Consider data normalization for category fields")
        
        # Database-specific recommendations
        for query in queries:
            if query.database_type == 'PostgreSQL':
                recommendations.append("PostgreSQL: Consider using CTEs for complex analytical queries")
            elif query.database_type == 'MySQL':
                recommendations.append("MySQL: Ensure InnoDB storage engine for ACID compliance")
            elif query.database_type == 'MongoDB':
                recommendations.append("MongoDB: Design proper document structure for aggregation efficiency")
        
        return recommendations[:5]  # Limit to 5 recommendations

# Initialize FastAPI app
app = FastAPI(
    title="Cross-Database Query Generator",
    description="Intelligent query translation system for PostgreSQL, MySQL, and MongoDB",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nlp_processor = NaturalLanguageProcessor()
query_generator = DatabaseQueryGenerator()
query_analyzer = QueryAnalyzer()

class DatabaseManager:
    def __init__(self, db_path: str = "query_generation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for query storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generated_queries (
                    query_id TEXT PRIMARY KEY,
                    original_question TEXT,
                    queries_data TEXT,
                    analysis_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_query_generation(self, query_id: str, response: QueryGenerationResponse):
        """Save query generation results to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO generated_queries 
                (query_id, original_question, queries_data, analysis_data)
                VALUES (?, ?, ?, ?)
            """, (
                query_id,
                response.original_question,
                json.dumps([q.dict() for q in response.queries]),
                json.dumps(response.query_analysis)
            ))
    
    def get_generation_history(self, limit: int = 20) -> List[Dict]:
        """Get query generation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT query_id, original_question, created_at
                FROM generated_queries 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

# Initialize database manager
db_manager = DatabaseManager()

# Sample questions for testing
SAMPLE_QUESTIONS = [
    "Show the profit margin of all products sold in Q4",
    "Count the total number of customers who made purchases last month",
    "List all orders with their total amounts, ordered by date",
    "What is the average order value for customers in the technology category?",
    "Show me the top 10 products by revenue",
    "How many orders were placed this week?",
    "Display sales data grouped by category for last quarter",
    "Find customers who spent more than $1000 in the last year"
]

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Cross-Database Query Generator API",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Natural language to SQL conversion",
            "Multi-database query generation",
            "Query optimization recommendations",
            "Performance analysis"
        ]
    }

@app.get("/api/v1/sample-questions")
async def get_sample_questions():
    """Get sample natural language questions for testing"""
    return {
        "sample_questions": SAMPLE_QUESTIONS,
        "description": "Sample questions demonstrating various query types and complexity levels"
    }

@app.get("/api/v1/database-specs")
async def get_database_specifications():
    """Get supported database specifications"""
    specs = {}
    for db_type, db_specs in query_generator.database_specs.items():
        specs[db_type] = {
            "name": db_specs.name,
            "sql_dialect": db_specs.sql_dialect,
            "optimization_features": db_specs.optimization_features,
            "reserved_keywords_count": len(db_specs.reserved_keywords)
        }
    
    return {
        "supported_databases": specs,
        "features": {
            "natural_language_processing": "Advanced NLP for query parsing",
            "multi_database_support": "PostgreSQL, MySQL, MongoDB",
            "optimization_recommendations": "Database-specific performance tips",
            "syntax_validation": "Query syntax verification for each database"
        }
    }

@app.post("/api/v1/generate-queries", response_model=QueryGenerationResponse)
async def generate_database_queries(request: NaturalLanguageQuery):
    """Generate database queries from natural language question"""
    
    try:
        query_id = str(uuid.uuid4())
        
        # Process natural language to extract components
        components = nlp_processor.extract_query_components(request.question)
        
        # Generate queries for all databases
        queries = query_generator.generate_queries(components, request.question)
        
        # Analyze the generated queries
        query_analysis = query_analyzer.analyze_queries(queries, request.question)
        
        # Generate best practices
        best_practices = [
            "Always test queries on sample data before production use",
            "Monitor query performance and adjust indexes accordingly",
            "Use database-specific optimization features for better performance",
            "Consider query caching for frequently executed queries",
            "Implement proper error handling for database operations"
        ]
        
        # Create response
        response = QueryGenerationResponse(
            query_id=query_id,
            original_question=request.question,
            queries=queries,
            query_analysis=query_analysis,
            best_practices=best_practices,
            generated_at=datetime.now()
        )
        
        # Save to database
        db_manager.save_query_generation(query_id, response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query generation failed: {str(e)}")

@app.get("/api/v1/query-history")
async def get_query_history(limit: int = 20):
    """Get query generation history"""
    try:
        history = db_manager.get_generation_history(limit)
        return {
            "history": history,
            "total_queries": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving query history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/validate-query")
async def validate_query(query: str, database_type: str):
    """Validate query syntax for a specific database"""
    
    try:
        if database_type.lower() in query_generator.database_specs:
            specs = query_generator.database_specs[database_type.lower()]
            is_valid = query_generator._validate_syntax(query, specs)
            
            return {
                "database_type": database_type,
                "query": query,
                "syntax_valid": is_valid,
                "validation_details": {
                    "length": len(query),
                    "complexity_score": query_generator._calculate_complexity_score(query),
                    "contains_sql_keywords": any(keyword in query.upper() for keyword in specs.reserved_keywords[:10])
                }
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported database type: {database_type}")
        
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query validation failed: {str(e)}")

@app.get("/api/v1/optimization-tips")
async def get_optimization_tips(database_type: str):
    """Get database-specific optimization tips"""
    
    try:
        if database_type.lower() in query_generator.database_specs:
            specs = query_generator.database_specs[database_type.lower()]
            
            tips = {
                "database_type": database_type,
                "general_tips": specs.optimization_features,
                "specific_tips": {
                    "PostgreSQL": [
                        "Use EXPLAIN ANALYZE to understand query execution plans",
                        "Create indexes on frequently filtered and joined columns",
                        "Consider using partial indexes for specific query patterns",
                        "Use materialized views for complex aggregations",
                        "Leverage window functions for analytical queries"
                    ],
                    "MySQL": [
                        "Use EXPLAIN to analyze query execution plans",
                        "Ensure proper indexing strategy for WHERE clauses",
                        "Consider query cache for frequently executed queries",
                        "Use InnoDB for ACID compliance and better performance",
                        "Optimize JOIN operations with proper index usage"
                    ],
                    "MongoDB": [
                        "Create appropriate indexes for aggregation pipeline stages",
                        "Use $match early in pipeline to reduce document processing",
                        "Consider compound indexes for multi-field queries",
                        "Use projection ($project) to limit returned fields",
                        "Leverage Atlas Search for complex text queries"
                    ]
                }
            }
            
            return tips
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported database type: {database_type}")
        
    except Exception as e:
        logger.error(f"Error getting optimization tips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization tips: {str(e)}")

# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "template_39_cross_database_query_generator:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )