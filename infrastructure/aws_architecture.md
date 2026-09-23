# AWS Infrastructure and Cloud Architecture

## Project

**Zero Trust Cloud Access Recommendation System for Government e-Services using Risk-Adaptive Intelligence**

This document describes the AWS infrastructure implemented for the project. The infrastructure provides authentication, API access, secure storage, encryption, monitoring, logging, and cloud-based request processing.

---

## 1. AWS Region

The project resources are deployed in:

- **AWS Region:** Asia Pacific (Mumbai)
- **Region Code:** `ap-south-1`

A monthly AWS budget was also configured to monitor project spending.

---

## 2. VPC and Network Architecture

A dedicated VPC was created for the project.

- **VPC Name:** `ZeroTrustProjectVPC`
- **VPC ID:** `vpc-00399a5233d202564`
- **IPv4 CIDR:** `10.0.0.0/16`
- **Default VPC:** No
- **DNS Resolution:** Enabled
- **DNS Hostnames:** Enabled

### Subnets

Three subnets were created:

| Subnet | CIDR | Purpose |
|---|---|---|
| `ZeroTrustPublicSubnet` | `10.0.1.0/24` | Public-facing resources |
| `ZeroTrustPrivateSubnet` | `10.0.2.0/24` | Private application resources |
| `ZeroTrustDataSubnet` | `10.0.3.0/24` | Data-related resources |

An Internet Gateway named `ZeroTrustInternetGateway` was attached to the VPC.

A public route table provides Internet Gateway routing for the public subnet.

A separate private route table is associated with the private subnet and does not contain a direct Internet Gateway route.

A NAT Gateway was not created in order to avoid unnecessary project costs.

---

## 3. Security Group

A security group named:

`ZeroTrustAppSecurityGroup`

was created for project resources.

The security group currently has:

- No inbound rules
- Default outbound rule

This provides a restrictive starting point for controlling network access.

---

## 4. Encryption with AWS KMS

A customer-managed AWS KMS key was created for project encryption.

- **Key alias:** `zero-trust-project`
- **Key type:** Symmetric
- **Key usage:** Encrypt and decrypt
- **Region:** Mumbai

The KMS key is used for encryption of supported project resources, including DynamoDB and S3.

---

## 5. Amazon Cognito

Amazon Cognito is used as the identity and authentication layer.

### User Pool

- **Name:** `User pool - 2v8rx4`
- **User Pool ID:** `ap-south-1_FxeQkW2MK`

The user pool is configured for email-based sign-in.

A test user was created for validating the authentication flow.

### MFA

Multi-factor authentication was configured using an authenticator application / TOTP mechanism.

MFA is configured as optional for the current development setup.

---

## 6. API Gateway

An Amazon API Gateway REST API was created for access requests.

### Endpoint structure

```text
POST /access/request
