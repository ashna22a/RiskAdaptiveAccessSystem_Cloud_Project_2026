# Zero Trust Cloud Access Recommendation System — Risk Engine

ML & risk-scoring component for the BCSE355L Cloud Architecture project:
*Zero Trust Cloud Access Recommendation System for Government e-Services
using Risk-Adaptive Intelligence*.

## What this repo does
- Synthesizes a government e-service access dataset (CSAD)
- Trains a Random Forest risk classifier (Allow / Challenge MFA / Deny)
- Serves predictions via SageMaker real-time endpoint
- Provides a rule + ML hybrid risk engine invoked by AWS Lambda
- Includes unit tests and endpoint latency benchmarks

## Quick start
See **RUN.md** section "Full Pipeline" for the end-to-end command sequence.
