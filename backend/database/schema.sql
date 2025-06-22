-- Raw Material Sourcing Workflow Database Schema
-- MySQL 8.0+ compatible

-- Create database
CREATE DATABASE IF NOT EXISTS sourcing_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE sourcing_db;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS workflow_execution_logs;
DROP TABLE IF EXISTS agent_interactions;
DROP TABLE IF EXISTS workflow_executions;
DROP TABLE IF EXISTS expert_analysis;
DROP TABLE IF EXISTS country_analysis;
DROP TABLE IF EXISTS raw_material_catalog;
DROP TABLE IF EXISTS business_requirement;

-- ===================================
-- Raw Material Catalog Table
-- ===================================
CREATE TABLE raw_material_catalog (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    material_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    description TEXT,
    
    -- Classification
    hs_code VARCHAR(20), -- Harmonized System code for trade
    industry_sector VARCHAR(100),
    perishable BOOLEAN DEFAULT FALSE,
    seasonal BOOLEAN DEFAULT FALSE,
    
    -- Global market data
    global_production_volume DECIMAL(15,2),
    production_unit VARCHAR(20) DEFAULT 'MT', -- Metric Tons
    major_producers JSON, -- Array of top producing countries
    major_consumers JSON, -- Array of top consuming countries
    
    -- Market characteristics
    price_volatility_index DECIMAL(3,1) DEFAULT 5.0 CHECK (price_volatility_index >= 0.0 AND price_volatility_index <= 10.0),
    quality_grades JSON, -- Different quality classifications
    storage_requirements TEXT,
    shelf_life_days INT,
    
    -- Sustainability metrics
    carbon_intensity DECIMAL(8,2), -- kg CO2 per unit
    water_footprint DECIMAL(10,2), -- liters per unit
    land_use_intensity DECIMAL(8,2), -- hectares per unit
    
    -- Metadata
    data_sources JSON,
    last_market_update DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_material_name (material_name),
    INDEX idx_category (category, subcategory),
    INDEX idx_hs_code (hs_code),
    INDEX idx_industry_sector (industry_sector)
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Catalog of raw materials with global market information';

-- ===================================
-- Core Business Requirements Table
-- ===================================
CREATE TABLE business_requirement (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    raw_material VARCHAR(100) DEFAULT 'general',
    destination_country VARCHAR(100) DEFAULT 'USA',
    
    -- Core scoring metrics
    cost_score DECIMAL(3,1) NOT NULL CHECK (cost_score >= 0.0 AND cost_score <= 10.0),
    stability_score DECIMAL(3,1) NOT NULL CHECK (stability_score >= 0.0 AND stability_score <= 10.0),
    eco_friendly_score DECIMAL(3,1) NOT NULL CHECK (eco_friendly_score >= 0.0 AND eco_friendly_score <= 10.0),
    
    -- Additional metrics
    quality_score DECIMAL(3,1) DEFAULT 7.0 CHECK (quality_score >= 0.0 AND quality_score <= 10.0),
    logistics_score DECIMAL(3,1) DEFAULT 7.0 CHECK (logistics_score >= 0.0 AND logistics_score <= 10.0),
    supplier_reliability DECIMAL(3,1) DEFAULT 7.0 CHECK (supplier_reliability >= 0.0 AND supplier_reliability <= 10.0),
    
    -- Economic data
    currency_code VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
    inflation_rate DECIMAL(5,2), -- Annual inflation percentage
    labor_cost_index DECIMAL(6,2), -- Relative to global average (100 = average)
    
    -- Risk assessment
    political_risk_rating ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    economic_risk_rating ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    operational_risk_rating ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    
    -- Trade information
    trade_agreement_status ENUM('NONE', 'BILATERAL', 'MULTILATERAL', 'PREFERENTIAL', 'FREE_TRADE') DEFAULT 'NONE',
    import_duty_rate DECIMAL(5,2) DEFAULT 0.00, -- Percentage
    trade_volume_annual DECIMAL(15,2), -- Annual trade value in USD
    
    -- Certifications and compliance
    certification_available JSON, -- Array of available certifications
    compliance_standards JSON, -- Array of compliance standards met
    quality_certifications JSON, -- ISO, etc.
    
    -- Production capacity
    production_capacity DECIMAL(15,2), -- Annual production capacity
    capacity_utilization DECIMAL(5,2) DEFAULT 80.00, -- Percentage
    export_capacity DECIMAL(15,2), -- Available for export
    
    -- Infrastructure
    port_facilities_rating DECIMAL(3,1) DEFAULT 7.0,
    transportation_rating DECIMAL(3,1) DEFAULT 7.0,
    communication_rating DECIMAL(3,1) DEFAULT 7.0,
    
    -- Metadata
    notes TEXT,
    data_source VARCHAR(200) DEFAULT 'Manual Entry',
    confidence_level ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
    verification_status ENUM('UNVERIFIED', 'PENDING', 'VERIFIED', 'DISPUTED') DEFAULT 'UNVERIFIED',
    verified_by VARCHAR(100),
    verified_at TIMESTAMP NULL,
    
    -- Timestamps
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_country (country),
    INDEX idx_raw_material (raw_material),
    INDEX idx_destination (destination_country),
    INDEX idx_scores (cost_score, stability_score, eco_friendly_score),
    INDEX idx_risk_ratings (political_risk_rating, economic_risk_rating, operational_risk_rating),
    INDEX idx_last_updated (last_updated),
    INDEX idx_verification (verification_status, verified_at),
    
    -- Composite indexes
    INDEX idx_country_material_dest (country, raw_material, destination_country),
    INDEX idx_material_scores (raw_material, cost_score DESC, stability_score DESC, eco_friendly_score DESC),
    
    -- Unique constraint to prevent duplicate entries
    UNIQUE KEY unique_country_material_dest (country, raw_material, destination_country)
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Business scoring requirements for countries and raw materials';

-- ===================================
-- Country Analysis Results Table
-- ===================================
CREATE TABLE country_analysis (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(100) NOT NULL UNIQUE, -- UUID for tracking
    country VARCHAR(100) NOT NULL,
    raw_material VARCHAR(100) NOT NULL,
    destination_country VARCHAR(100) DEFAULT 'USA',
    agent_id VARCHAR(200),
    workflow_execution_id INT UNSIGNED,
    
    -- Research phase data
    search_queries JSON, -- Array of search queries used
    search_results_summary TEXT, -- Consolidated search results
    research_data_quality ENUM('POOR', 'FAIR', 'GOOD', 'EXCELLENT') DEFAULT 'FAIR',
    research_completion_rate DECIMAL(5,2) DEFAULT 100.00, -- Percentage of planned research completed
    
    -- Analysis phase data
    claude_analysis_prompt TEXT, -- The prompt sent to Claude
    claude_analysis_response TEXT, -- Full Claude response
    claude_tokens_used INT DEFAULT 0,
    claude_model_used VARCHAR(50) DEFAULT 'claude-3-sonnet-20240229',
    
    -- Expert coordination
    expert_fields_analyzed JSON, -- Array of expert fields that analyzed this country
    expert_coordination_summary JSON, -- Summary of expert interactions
    expert_consensus_score DECIMAL(3,1), -- Consensus score from experts
    expert_disagreement_areas JSON, -- Areas where experts disagreed
    
    -- Derived analysis results
    derived_scores JSON, -- The scores derived from analysis
    score_calculation_method VARCHAR(100) DEFAULT 'weighted_average',
    score_confidence DECIMAL(3,1) DEFAULT 7.0,
    
    -- Strengths and weaknesses
    identified_strengths JSON, -- Array of strength descriptions
    identified_weaknesses JSON, -- Array of weakness descriptions
    risk_factors JSON, -- Array of identified risks
    mitigation_strategies JSON, -- Suggested risk mitigation approaches
    
    -- Recommendations
    sourcing_recommendations JSON, -- Array of specific recommendations
    implementation_timeline VARCHAR(500), -- Suggested timeline for implementation
    next_steps JSON, -- Array of recommended next steps
    alternative_options JSON, -- Alternative sourcing options
    
    -- Assessment summary
    overall_assessment TEXT, -- Comprehensive assessment summary
    recommendation_category ENUM('HIGHLY_RECOMMENDED', 'RECOMMENDED', 'CONDITIONAL', 'NOT_RECOMMENDED') DEFAULT 'CONDITIONAL',
    confidence_justification TEXT, -- Why this confidence level was assigned
    
    -- Performance metrics
    analysis_depth_score DECIMAL(3,1) DEFAULT 7.0, -- How thorough was the analysis
    data_quality_score DECIMAL(3,1) DEFAULT 7.0, -- Quality of underlying data
    methodology_score DECIMAL(3,1) DEFAULT 7.0, -- Quality of analysis methodology
    
    -- Execution metadata
    execution_time_seconds DECIMAL(8,3),
    memory_usage_mb DECIMAL(8,2),
    error_count INT DEFAULT 0,
    warning_count INT DEFAULT 0,
    
    -- Status tracking
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', 'CANCELLED') DEFAULT 'COMPLETED',
    completion_percentage DECIMAL(5,2) DEFAULT 100.00,
    error_message TEXT,
    warnings JSON, -- Array of warning messages
    
    -- Audit trail
    created_by VARCHAR(100) DEFAULT 'system',
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP NULL,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP NULL,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_country_material (country, raw_material),
    INDEX idx_destination (destination_country),
    INDEX idx_workflow_execution (workflow_execution_id),
    INDEX idx_status (status),
    INDEX idx_recommendation (recommendation_category),
    INDEX idx_agent_id (agent_id),
    INDEX idx_created_at (created_at),
    INDEX idx_completion_time (completed_at),
    
    -- Composite indexes
    INDEX idx_country_material_status (country, raw_material, status),
    INDEX idx_workflow_country (workflow_execution_id, country),
    
    -- Foreign key constraints
    CONSTRAINT fk_country_analysis_workflow 
        FOREIGN KEY (workflow_execution_id) 
        REFERENCES workflow_executions(id) 
        ON DELETE SET NULL ON UPDATE CASCADE
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Detailed country analysis results from country agents';

-- ===================================
-- Expert Analysis Results Table
-- ===================================
CREATE TABLE expert_analysis (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(100) NOT NULL, -- UUID for tracking
    expertise_field ENUM('eco-friendly', 'profitability', 'stability', 'quality', 'logistics', 'compliance') NOT NULL,
    country VARCHAR(100) NOT NULL,
    raw_material VARCHAR(100) NOT NULL,
    destination_country VARCHAR(100) DEFAULT 'USA',
    agent_id VARCHAR(200),
    country_analysis_id INT UNSIGNED, -- Link to country analysis
    workflow_execution_id INT UNSIGNED,
    
    -- Research phase
    specialized_queries JSON, -- Domain-specific search queries
    research_focus_areas JSON, -- Areas of research focus
    research_sources JSON, -- Sources of information used
    research_quality_rating DECIMAL(3,1) DEFAULT 7.0,
    
    -- Domain expertise data
    domain_knowledge_applied JSON, -- Which knowledge areas were used
    analysis_methodology VARCHAR(200), -- Methodology used for analysis
    benchmarking_data JSON, -- Benchmark data used for comparison
    industry_standards JSON, -- Relevant industry standards considered
    
    -- Expert analysis
    detailed_findings TEXT, -- Comprehensive findings
    quantitative_metrics JSON, -- Numerical metrics identified
    qualitative_insights JSON, -- Qualitative observations
    comparative_analysis TEXT, -- Comparison with other options
    
    -- Scoring and assessment
    expert_score DECIMAL(3,1) NOT NULL CHECK (expert_score >= 0.0 AND expert_score <= 10.0),
    score_components JSON, -- Breakdown of how score was calculated
    scoring_methodology VARCHAR(200), -- Method used for scoring
    score_confidence DECIMAL(3,1) DEFAULT 7.0,
    score_justification TEXT, -- Detailed justification for the score
    
    -- Risk and opportunity analysis
    identified_risks JSON, -- Domain-specific risks identified
    risk_severity_ratings JSON, -- Severity ratings for each risk
    opportunities JSON, -- Opportunities identified
    opportunity_potential JSON, -- Potential impact of opportunities
    
    -- Recommendations
    expert_recommendations JSON, -- Expert's specific recommendations
    best_practices JSON, -- Recommended best practices
    implementation_guidance TEXT, -- How to implement recommendations
    monitoring_requirements JSON, -- What should be monitored
    
    -- Peer validation
    peer_review_requested BOOLEAN DEFAULT FALSE,
    peer_reviewer VARCHAR(100),
    peer_review_score DECIMAL(3,1),
    peer_review_comments TEXT,
    peer_review_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'REVISED') DEFAULT 'PENDING',
    
    -- Performance metrics
    analysis_depth DECIMAL(3,1) DEFAULT 7.0, -- Depth of analysis
    evidence_quality DECIMAL(3,1) DEFAULT 7.0, -- Quality of supporting evidence
    methodology_rigor DECIMAL(3,1) DEFAULT 7.0, -- Rigor of methodology
    
    -- Execution data
    claude_prompts_used JSON, -- Prompts sent to Claude for this analysis
    claude_responses JSON, -- Responses received from Claude
    claude_tokens_consumed INT DEFAULT 0,
    search_queries_executed JSON, -- Search queries executed
    database_queries_executed JSON, -- Database queries executed
    
    -- Metadata
    execution_time_seconds DECIMAL(8,3),
    resource_usage JSON, -- Resource usage statistics
    error_log JSON, -- Any errors encountered
    warning_log JSON, -- Any warnings generated
    
    -- Status and quality control
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'UNDER_REVIEW', 'APPROVED') DEFAULT 'COMPLETED',
    quality_score DECIMAL(3,1) DEFAULT 7.0, -- Overall quality of analysis
    completeness_percentage DECIMAL(5,2) DEFAULT 100.00,
    validation_status ENUM('UNVALIDATED', 'VALIDATED', 'DISPUTED', 'REQUIRES_REVISION') DEFAULT 'UNVALIDATED',
    
    -- Audit trail
    created_by VARCHAR(100) DEFAULT 'system',
    validated_by VARCHAR(100),
    validated_at TIMESTAMP NULL,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_expertise_field (expertise_field),
    INDEX idx_country_material (country, raw_material),
    INDEX idx_expert_score (expert_score DESC),
    INDEX idx_country_analysis (country_analysis_id),
    INDEX idx_workflow_execution (workflow_execution_id),
    INDEX idx_status_validation (status, validation_status),
    INDEX idx_agent_id (agent_id),
    INDEX idx_created_at (created_at),
    
    -- Composite indexes
    INDEX idx_field_country_material (expertise_field, country, raw_material),
    INDEX idx_workflow_field (workflow_execution_id, expertise_field),
    INDEX idx_score_confidence (expert_score DESC, score_confidence DESC),
    
    -- Unique constraint to prevent duplicate expert analysis
    UNIQUE KEY unique_expert_country_material (expertise_field, country, raw_material, destination_country, workflow_execution_id),
    
    -- Foreign key constraints
    CONSTRAINT fk_expert_analysis_country 
        FOREIGN KEY (country_analysis_id) 
        REFERENCES country_analysis(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_expert_analysis_workflow 
        FOREIGN KEY (workflow_execution_id) 
        REFERENCES workflow_executions(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Expert analysis results by domain specialists';

-- ===================================
-- Workflow Executions Table
-- ===================================
CREATE TABLE workflow_executions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(100) NOT NULL UNIQUE, -- UUID for tracking
    
    -- Input parameters
    raw_material VARCHAR(100) NOT NULL,
    destination_country VARCHAR(100) NOT NULL,
    requester VARCHAR(100) DEFAULT 'system',
    execution_context JSON, -- Additional context parameters
    
    -- Workflow configuration
    workflow_version VARCHAR(20) DEFAULT '1.0',
    agent_configuration JSON, -- Configuration used for agents
    scoring_weights JSON, -- Weights used for final scoring
    analysis_depth ENUM('BASIC', 'STANDARD', 'COMPREHENSIVE', 'DETAILED') DEFAULT 'STANDARD',
    
    -- Results summary
    countries_analyzed JSON, -- List of countries that were analyzed
    recommended_country VARCHAR(100),
    recommended_country_score DECIMAL(3,1),
    alternative_countries JSON, -- Alternative options with scores
    
    -- Detailed results
    leader_analysis_summary JSON, -- Summary from leader agent
    country_analysis_summary JSON, -- Summary from country agents
    expert_analysis_summary JSON, -- Summary from expert agents
    final_recommendation TEXT, -- Complete final recommendation
    
    -- Risk assessment
    overall_risk_rating ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    risk_factors JSON, -- Key risk factors identified
    risk_mitigation_strategies JSON, -- Suggested mitigation strategies
    
    -- Implementation guidance
    implementation_timeline JSON, -- Suggested implementation phases
    next_steps JSON, -- Recommended next steps
    success_factors JSON, -- Key success factors
    monitoring_requirements JSON, -- What should be monitored
    
    -- Quality metrics
    analysis_completeness DECIMAL(5,2) DEFAULT 100.00, -- Percentage of planned analysis completed
    data_quality_score DECIMAL(3,1) DEFAULT 7.0, -- Overall data quality
    confidence_level ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
    reliability_score DECIMAL(3,1) DEFAULT 7.0, -- Reliability of recommendations
    
    -- Performance metrics
    total_execution_time_seconds DECIMAL(10,3),
    leader_agent_time DECIMAL(8,3),
    country_agents_time DECIMAL(8,3),
    expert_agents_time DECIMAL(8,3),
    
    -- Resource usage
    total_api_calls INT DEFAULT 0,
    total_tokens_used INT DEFAULT 0,
    database_queries_executed INT DEFAULT 0,
    search_queries_executed INT DEFAULT 0,
    
    -- Agent statistics
    agents_deployed JSON, -- List of agents deployed
    successful_agents INT DEFAULT 0,
    failed_agents INT DEFAULT 0,
    agent_coordination_issues JSON, -- Any coordination problems
    
    -- Status tracking
    status ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'PARTIAL_SUCCESS') DEFAULT 'COMPLETED',
    completion_percentage DECIMAL(5,2) DEFAULT 100.00,
    current_phase ENUM('INITIALIZATION', 'LEADER_ANALYSIS', 'COUNTRY_ANALYSIS', 'EXPERT_ANALYSIS', 'SYNTHESIS', 'FINALIZATION') DEFAULT 'FINALIZATION',
    
    -- Error handling
    error_count INT DEFAULT 0,
    warning_count INT DEFAULT 0,
    error_details JSON, -- Detailed error information
    warning_details JSON, -- Warning messages
    recovery_actions JSON, -- Actions taken to recover from errors
    
    -- Business impact
    estimated_cost_savings DECIMAL(15,2), -- Estimated annual cost savings
    estimated_roi_percentage DECIMAL(5,2), -- Estimated ROI percentage
    business_impact_category ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    strategic_importance ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    
    -- Audit and compliance
    approval_required BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP NULL,
    approval_comments TEXT,
    compliance_checks JSON, -- Compliance verification results
    
    -- Feedback and follow-up
    user_feedback_score DECIMAL(3,1), -- User satisfaction score
    user_feedback_comments TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    
    -- Timestamps
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_execution_id (execution_id),
    INDEX idx_raw_material (raw_material),
    INDEX idx_destination_country (destination_country),
    INDEX idx_recommended_country (recommended_country),
    INDEX idx_status (status),
    INDEX idx_requester (requester),
    INDEX idx_completion_time (completed_at),
    INDEX idx_approval (approval_required, approved_by),
    INDEX idx_follow_up (follow_up_required, follow_up_date),
    
    -- Composite indexes
    INDEX idx_material_destination (raw_material, destination_country),
    INDEX idx_status_phase (status, current_phase),
    INDEX idx_performance (total_execution_time_seconds, completion_percentage)
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Complete workflow execution tracking and results';

-- ===================================
-- Agent Interactions Table
-- ===================================
CREATE TABLE agent_interactions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    interaction_id VARCHAR(100) NOT NULL, -- UUID for this interaction
    workflow_execution_id INT UNSIGNED NOT NULL,
    
    -- Agent information
    source_agent_type ENUM('leader', 'country', 'expert', 'coordinator') NOT NULL,
    source_agent_id VARCHAR(200) NOT NULL,
    target_agent_type ENUM('leader', 'country', 'expert', 'coordinator', 'tool', 'external'),
    target_agent_id VARCHAR(200),
    
    -- Interaction details
    interaction_type ENUM('DELEGATION', 'COORDINATION', 'DATA_REQUEST', 'RESULT_SHARING', 'ERROR_REPORTING', 'STATUS_UPDATE') NOT NULL,
    interaction_purpose TEXT, -- Purpose of this interaction
    
    -- Message content
    message_content TEXT, -- The actual message/data exchanged
    message_format ENUM('TEXT', 'JSON', 'XML', 'BINARY') DEFAULT 'TEXT',
    message_size_bytes INT DEFAULT 0,
    
    -- Request/Response tracking
    request_data JSON, -- Data sent in request
    response_data JSON, -- Data received in response
    response_status ENUM('SUCCESS', 'PARTIAL', 'FAILED', 'TIMEOUT', 'CANCELLED') DEFAULT 'SUCCESS',
    
    -- Performance metrics
    latency_milliseconds INT DEFAULT 0, -- Time taken for interaction
    retry_count INT DEFAULT 0,
    timeout_occurred BOOLEAN DEFAULT FALSE,
    
    -- Quality metrics
    data_quality_score DECIMAL(3,1) DEFAULT 7.0,
    interaction_success_score DECIMAL(3,1) DEFAULT 8.0,
    
    -- Error handling
    error_code VARCHAR(50),
    error_message TEXT,
    resolution_applied TEXT,
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_interaction_id (interaction_id),
    INDEX idx_workflow_execution (workflow_execution_id),
    INDEX idx_source_agent (source_agent_type, source_agent_id),
    INDEX idx_target_agent (target_agent_type, target_agent_id),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_response_status (response_status),
    INDEX idx_initiated_at (initiated_at),
    
    -- Foreign key constraints
    CONSTRAINT fk_agent_interactions_workflow 
        FOREIGN KEY (workflow_execution_id) 
        REFERENCES workflow_executions(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Tracking of all agent-to-agent interactions';

-- ===================================
-- Workflow Execution Logs Table
-- ===================================
CREATE TABLE workflow_execution_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    workflow_execution_id INT UNSIGNED NOT NULL,
    
    -- Log entry details
    log_level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    log_category ENUM('SYSTEM', 'AGENT', 'TOOL', 'DATABASE', 'API', 'BUSINESS') DEFAULT 'SYSTEM',
    component VARCHAR(100), -- Which component generated the log
    
    -- Message information
    message TEXT NOT NULL,
    message_code VARCHAR(50), -- Standardized message code
    details JSON, -- Additional structured details
    
    -- Context information
    agent_id VARCHAR(200),
    tool_name VARCHAR(100),
    operation VARCHAR(100),
    
    -- Performance data
    execution_time_ms INT,
    memory_usage_mb DECIMAL(8,2),
    
    -- Error information (if applicable)
    error_type VARCHAR(100),
    stack_trace TEXT,
    resolution_status ENUM('UNRESOLVED', 'RESOLVED', 'IGNORED', 'ESCALATED') DEFAULT 'UNRESOLVED',
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_workflow_execution (workflow_execution_id),
    INDEX idx_log_level (log_level),
    INDEX idx_log_category (log_category),
    INDEX idx_component (component),
    INDEX idx_agent_id (agent_id),
    INDEX idx_created_at (created_at),
    INDEX idx_error_resolution (error_type, resolution_status),
    
    -- Composite indexes
    INDEX idx_workflow_level_time (workflow_execution_id, log_level, created_at),
    
    -- Foreign key constraints
    CONSTRAINT fk_execution_logs_workflow 
        FOREIGN KEY (workflow_execution_id) 
        REFERENCES workflow_executions(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Detailed execution logs for workflow debugging and monitoring';

-- ===================================
-- Insert Sample Data
-- ===================================

-- Insert raw material catalog data
INSERT INTO raw_material_catalog (
    material_name, category, subcategory, description, hs_code, industry_sector,
    perishable, seasonal, global_production_volume, production_unit,
    major_producers, major_consumers, price_volatility_index,
    carbon_intensity, water_footprint, land_use_intensity
) VALUES 
('Cocoa Beans', 'Agricultural', 'Tree Crops', 'Raw cocoa beans for chocolate production', '180100', 'Food & Beverage', FALSE, TRUE, 5200000, 'MT',
 '["Ivory Coast", "Ghana", "Ecuador", "Nigeria", "Brazil"]', '["Germany", "Netherlands", "USA", "Malaysia", "Belgium"]', 7.5,
 2.30, 21000, 4.5),
 
('Coffee Beans', 'Agricultural', 'Tree Crops', 'Green coffee beans for processing', '090111', 'Food & Beverage', FALSE, TRUE, 10200000, 'MT',
 '["Brazil", "Vietnam", "Colombia", "Indonesia", "Ethiopia"]', '["USA", "Germany", "Japan", "Italy", "France"]', 8.2,
 1.80, 18700, 2.8),
 
('Cotton', 'Agricultural', 'Fiber Crops', 'Raw cotton fiber for textile production', '520100', 'Textile', FALSE, TRUE, 25800000, 'MT',
 '["China", "India", "USA", "Brazil", "Pakistan"]', '["China", "India", "Pakistan", "Turkey", "Brazil"]', 6.8,
 5.90, 10000, 2.5),
 
('Raw Sugar', 'Agricultural', 'Sugar Crops', 'Raw sugar cane for refining', '170111', 'Food & Beverage', FALSE, TRUE, 185000000, 'MT',
 '["Brazil", "India", "Thailand", "China", "USA"]', '["India", "China", "USA", "Brazil", "Russia"]', 7.0,
 0.50, 1800, 0.6);

-- Insert business requirement data with comprehensive scoring
INSERT INTO business_requirement (
    country, raw_material, destination_country, cost_score, stability_score, eco_friendly_score,
    quality_score, logistics_score, supplier_reliability, currency_code, political_risk_rating,
    economic_risk_rating, trade_agreement_status, import_duty_rate, certification_available,
    production_capacity, export_capacity, port_facilities_rating, transportation_rating,
    confidence_level, verification_status, data_source
) VALUES 
-- Cocoa producing countries
('Ecuador', 'Cocoa Beans', 'USA', 8.5, 6.0, 7.5, 9.0, 7.8, 8.2, 'USD', 'MEDIUM', 'MEDIUM', 'BILATERAL', 0.00, 
 '["Organic", "Fair Trade", "Rainforest Alliance"]', 280000, 250000, 7.5, 8.0, 'HIGH', 'VERIFIED', 'Industry Report 2024'),

('Ghana', 'Cocoa Beans', 'USA', 7.0, 7.5, 8.0, 8.5, 8.2, 8.8, 'GHS', 'LOW', 'MEDIUM', 'PREFERENTIAL', 0.00,
 '["Fair Trade", "UTZ", "Organic"]', 850000, 800000, 8.0, 7.5, 'HIGH', 'VERIFIED', 'Trade Association Data'),

('Ivory Coast', 'Cocoa Beans', 'USA', 6.5, 6.5, 6.0, 7.5, 7.0, 7.2, 'XOF', 'MEDIUM', 'MEDIUM', 'PREFERENTIAL', 0.00,
 '["UTZ", "Rainforest Alliance"]', 2100000, 2000000, 7.2, 6.8, 'MEDIUM', 'VERIFIED', 'Government Statistics'),

-- Coffee producing countries  
('Brazil', 'Coffee Beans', 'USA', 7.5, 6.8, 7.2, 8.0, 8.5, 8.0, 'BRL', 'LOW', 'MEDIUM', 'NONE', 0.00,
 '["Organic", "Fair Trade", "4C"]', 3200000, 2800000, 8.8, 8.2, 'HIGH', 'VERIFIED', 'Coffee Board Data'),

('Colombia', 'Coffee Beans', 'USA', 8.0, 6.2, 7.8, 9.2, 8.0, 8.5, 'COP', 'MEDIUM', 'MEDIUM', 'FREE_TRADE', 0.00,
 '["Organic", "Fair Trade", "Rainforest Alliance"]', 850000, 700000, 8.0, 7.8, 'HIGH', 'VERIFIED', 'FNC Statistics'),

('Ethiopia', 'Coffee Beans', 'USA', 9.0, 5.5, 6.5, 8.8, 6.5, 7.0, 'ETB', 'MEDIUM', 'HIGH', 'PREFERENTIAL', 0.00,
 '["Organic", "Fair Trade"]', 470000, 200000, 6.0, 6.2, 'MEDIUM', 'PENDING', 'Export Authority'),

-- Cotton producing countries
('India', 'Cotton', 'USA', 8.8, 6.5, 6.0, 7.5, 7.2, 7.8, 'INR', 'LOW', 'MEDIUM', 'NONE', 8.40,
 '["GOTS", "OCS", "Better Cotton"]', 6200000, 1200000, 7.8, 7.5, 'HIGH', 'VERIFIED', 'Cotton Corporation'),

('Vietnam', 'Cotton', 'USA', 8.2, 7.0, 6.8, 7.8, 8.0, 8.2, 'VND', 'LOW', 'LOW', 'NONE', 0.00,
 '["Better Cotton", "GOTS"]', 350000, 280000, 8.2, 8.5, 'HIGH', 'VERIFIED', 'Ministry of Agriculture'),

-- Sugar producing countries
('Thailand', 'Raw Sugar', 'USA', 7.8, 7.2, 7.0, 8.2, 8.5, 8.0, 'THB', 'LOW', 'LOW', 'NONE', 0.50,
 '["Organic", "Bonsucro"]', 11500000, 8500000, 8.8, 8.2, 'HIGH', 'VERIFIED', 'Sugar Board Thailand'),

('Indonesia', 'Raw Sugar', 'USA', 8.1, 6.8, 6.7, 7.5, 7.8, 7.5, 'IDR', 'MEDIUM', 'MEDIUM', 'NONE', 5.00,
 '["Bonsucro"]', 2800000, 800000, 7.5, 7.2, 'MEDIUM', 'VERIFIED', 'Sugar Association');

-- ===================================
-- Create Views for Common Queries
-- ===================================

-- View for best countries by raw material
CREATE VIEW v_best_countries_by_material AS
SELECT 
    raw_material,
    country,
    destination_country,
    ROUND((cost_score * 0.3 + stability_score * 0.25 + eco_friendly_score * 0.25 + 
           quality_score * 0.1 + logistics_score * 0.05 + supplier_reliability * 0.05), 2) AS composite_score,
    cost_score,
    stability_score, 
    eco_friendly_score,
    quality_score,
    logistics_score,
    supplier_reliability,
    political_risk_rating,
    economic_risk_rating,
    trade_agreement_status,
    certification_available,
    last_updated
FROM business_requirement
WHERE verification_status = 'VERIFIED'
ORDER BY raw_material, composite_score DESC;

-- View for workflow execution summary
CREATE VIEW v_workflow_execution_summary AS
SELECT 
    we.id,
    we.execution_id,
    we.raw_material,
    we.destination_country,
    we.recommended_country,
    we.recommended_country_score,
    we.status,
    we.confidence_level,
    we.total_execution_time_seconds,
    we.analysis_completeness,
    we.successful_agents,
    we.failed_agents,
    we.total_api_calls,
    we.total_tokens_used,
    COUNT(ca.id) as country_analyses_count,
    COUNT(ea.id) as expert_analyses_count,
    we.requested_at,
    we.completed_at
FROM workflow_executions we
LEFT JOIN country_analysis ca ON we.id = ca.workflow_execution_id
LEFT JOIN expert_analysis ea ON we.id = ea.workflow_execution_id
GROUP BY we.id
ORDER BY we.completed_at DESC;

-- View for expert analysis performance
CREATE VIEW v_expert_analysis_performance AS
SELECT 
    expertise_field,
    country,
    raw_material,
    AVG(expert_score) as avg_expert_score,
    AVG(score_confidence) as avg_confidence,
    AVG(analysis_depth) as avg_analysis_depth,
    COUNT(*) as total_analyses,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as successful_analyses,
    AVG(execution_time_seconds) as avg_execution_time,
    MAX(completed_at) as last_analysis_date
FROM expert_analysis
GROUP BY expertise_field, country, raw_material
ORDER BY expertise_field, avg_expert_score DESC;

-- ===================================
-- Create Stored Procedures
-- ===================================

DELIMITER //

-- Procedure to get country ranking for a specific material
CREATE PROCEDURE GetCountryRanking(
    IN p_raw_material VARCHAR(100),
    IN p_destination_country VARCHAR(100) DEFAULT 'USA',
    IN p_limit INT DEFAULT 10
)
BEGIN
    SELECT 
        country,
        ROUND((cost_score * 0.3 + stability_score * 0.25 + eco_friendly_score * 0.25 + 
               quality_score * 0.1 + logistics_score * 0.05 + supplier_reliability * 0.05), 2) AS composite_score,
        cost_score,
        stability_score,
        eco_friendly_score,
        quality_score,
        logistics_score,
        supplier_reliability,
        political_risk_rating,
        economic_risk_rating,
        trade_agreement_status,
        import_duty_rate,
        certification_available,
        production_capacity,
        export_capacity,
        last_updated
    FROM business_requirement
    WHERE raw_material = p_raw_material 
      AND destination_country = p_destination_country
      AND verification_status = 'VERIFIED'
    ORDER BY composite_score DESC
    LIMIT p_limit;
END //

-- Procedure to log workflow execution
CREATE PROCEDURE LogWorkflowExecution(
    IN p_workflow_execution_id INT,
    IN p_log_level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
    IN p_component VARCHAR(100),
    IN p_message TEXT,
    IN p_details JSON DEFAULT NULL,
    IN p_agent_id VARCHAR(200) DEFAULT NULL
)
BEGIN
    INSERT INTO workflow_execution_logs (
        workflow_execution_id, log_level, component, message, details, agent_id
    ) VALUES (
        p_workflow_execution_id, p_log_level, p_component, p_message, p_details, p_agent_id
    );
END //

DELIMITER ;

-- ===================================
-- Create Triggers for Audit Trail
-- ===================================

DELIMITER //

-- Trigger to update workflow execution stats when country analysis is inserted
CREATE TRIGGER tr_country_analysis_insert 
AFTER INSERT ON country_analysis
FOR EACH ROW
BEGIN
    UPDATE workflow_executions 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.workflow_execution_id;
END //

-- Trigger to update workflow execution stats when expert analysis is inserted  
CREATE TRIGGER tr_expert_analysis_insert
AFTER INSERT ON expert_analysis  
FOR EACH ROW
BEGIN
    UPDATE workflow_executions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.workflow_execution_id;
END //

DELIMITER ;

-- ===================================
-- Performance Optimization
-- ===================================

-- Analyze tables for query optimization
ANALYZE TABLE business_requirement;
ANALYZE TABLE country_analysis;
ANALYZE TABLE expert_analysis;
ANALYZE TABLE workflow_executions;
ANALYZE TABLE agent_interactions;
ANALYZE TABLE workflow_execution_logs;

-- Set some MySQL optimizations
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB (adjust based on available memory)
SET GLOBAL query_cache_size = 67108864; -- 64MB
SET GLOBAL max_connections = 200;

-- ===================================
-- Security Settings
-- ===================================

-- Create application user with limited privileges
CREATE USER IF NOT EXISTS 'sourcing_app'@'localhost' IDENTIFIED BY 'secure_password_2024!';
CREATE USER IF NOT EXISTS 'sourcing_readonly'@'localhost' IDENTIFIED BY 'readonly_password_2024!';

-- Grant appropriate privileges
GRANT SELECT, INSERT, UPDATE ON sourcing_db.* TO 'sourcing_app'@'localhost';
GRANT SELECT ON sourcing_db.* TO 'sourcing_readonly'@'localhost';

-- Grant execute permission on stored procedures
GRANT EXECUTE ON PROCEDURE sourcing_db.GetCountryRanking TO 'sourcing_app'@'localhost';
GRANT EXECUTE ON PROCEDURE sourcing_db.LogWorkflowExecution TO 'sourcing_app'@'localhost';

-- ===================================
-- Backup and Maintenance Setup
-- ===================================

-- Create events for automated maintenance (requires event scheduler to be enabled)
-- SET GLOBAL event_scheduler = ON;

DELIMITER //

-- Event to clean old workflow execution logs (keep only last 90 days)
CREATE EVENT IF NOT EXISTS ev_cleanup_old_logs
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    DELETE FROM workflow_execution_logs 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
END //

-- Event to update statistics tables daily  
CREATE EVENT IF NOT EXISTS ev_update_statistics
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP  
DO
BEGIN
    ANALYZE TABLE business_requirement;
    ANALYZE TABLE country_analysis;
    ANALYZE TABLE expert_analysis;
    ANALYZE TABLE workflow_executions;
END //

DELIMITER ;

-- ===================================
-- Final Setup Confirmation
-- ===================================

-- Show created tables
SHOW TABLES;

-- Show table status
SELECT 
    TABLE_NAME,
    ENGINE,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    CREATE_TIME
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'sourcing_db'
ORDER BY TABLE_NAME;

-- Show sample data counts
SELECT 'raw_material_catalog' as table_name, COUNT(*) as row_count FROM raw_material_catalog
UNION ALL
SELECT 'business_requirement', COUNT(*) FROM business_requirement  
UNION ALL
SELECT 'country_analysis', COUNT(*) FROM country_analysis
UNION ALL
SELECT 'expert_analysis', COUNT(*) FROM expert_analysis
UNION ALL
SELECT 'workflow_executions', COUNT(*) FROM workflow_executions;

-- Display successful setup message
SELECT 'Raw Material Sourcing Database Setup Complete!' as status,
       'All tables, views, procedures, and sample data have been created successfully.' as message;