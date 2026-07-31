Project Title: Zero Trust Cloud Access Recommendation System for Government e- Services using Risk-Adaptive Intelligence

Team Members:
1. Ashna Agarwal (24BIT0249)
2. Krithikha B (24BIT0545)

Problem Statement:
Government e-services transitioning to cloud environments face critical security challenges as traditional perimeter-based security models prove inadequate against evolving cyber threats. Current access control systems rely on static authentication and authorization policies that fail to adapt to changing risk contexts, user behavior patterns, and real-time threat intelligence.

Objectives:
1. Develop a risk adaptive access recommendation system
2. Implement continuous authentication and zero trust verification
3. Create a risk scoring engine
4. Build a monitoring and alerting dashboard
5. Design a scalable cloud architecture
6. Establish secure data storage

Proposed Framework:
The system follows a serverless, microservices-based architecture with five key layers:
1. User Access Layer
2. Identity Verification Layer
3. Risk Assessment Engine
4. Access Recommendation Engine
5. Policy Enforcement and Monitoring

Technology Stack:
Amazon Cognito:	Identity management and Authentication
Amazon API Gateway:	REST API exposure and rate limiting
AWS Lambda: Serverless compute for risk scoring and access decisions
Amazon SageMaker: Model training, deployment, and inference
Amazon DynamoDB: User profiles and risk scores storage
Amazon CloudWatch: System metrics, alarms, and dashboards
AWS CloudTrail: API call logging and compliance

Dataset:
Cloud Access Security Dataset (CASD)
Source: Synthesized from public cloud security datasets and government access patterns
Size: 50,000-10,000 records
Features: 15 features (5 categorical, 7 numerical, 3 binary)
