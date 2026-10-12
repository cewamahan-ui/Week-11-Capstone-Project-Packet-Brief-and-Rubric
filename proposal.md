# Module 4 Capstone: AfyaPlus Project Proposal

## Project Path Chosen
AfyaPlus Module 4 Capstone (recommended path)

## Problem Statement
The healthcare system faces critical challenges in efficient patient triage, catalog management, and AI-assisted decision support. Clinics need an integrated platform that combines:
- Automated patient symptom assessment and routing
- Intelligent medical catalog management with version control  
- Secure, compliant AI operations for healthcare delivery
- Real-time performance monitoring and cost tracking

## Dataset Scale
Teaching fixture dataset of approximately 300 synthetic rows (200-500 range as required) in `fixtures/triage_messages_sample.jsonl`. This synthetic dataset contains realistic patient triage messages without real clinical PII, suitable for demonstrating the system's capabilities while maintaining teaching constraints.

## Project Milestones
1. **Core Integration (Week 11)**: Deploy end-to-end system with stubbed LLM/MCP components
2. **Testing Implementation**: Complete unit tests, security smoke tests, and integration testing
3. **Documentation Completion**: Create comprehensive architecture, deployment, and user guides
4. **Peer Review and Validation**: Execute peer review process and gather feedback

## Milestones Out of Scope
- Live OpenAI API integration (stubs used)
- Full cloud deployment (deployment docs only)
- Production-level scalability testing
- Real-time streaming features

## Technical Architecture
The system integrates multiple components:
- **Router Service**: Intelligent request routing using deterministic logic
- **RAG System**: Retrieval-augmented generation with document processing
- **MCP Tools**: Model context protocol stubs for AI operations
- **Security Layer**: PII redaction and compliance controls
- **Pins/Versioning**: Component version tracking and deployment management
- **Catalog System**: Medical catalog with search and filtering
- **Triage Service**: Patient symptom assessment and routing

## Budget Constraints
- Unit testing and stubs: $0
- Golden-set evaluation (stubs): $0  
- Live demo calls: ~$1.00 (10 API calls)
- Teaching cost tables included in cost_analysis.md

## Deployment Approach
- Local development using pytest and httpx
- Manual testing without Docker
- Self-review with feature branch workflow
- Stub agents for LLM/MCP components
- Comprehensive fallback mechanisms for missing dependencies

## Skill Coverage Week Reuse
Based on skill_matrix.md, this project demonstrates proficiency in:
- Weeks 1-5: LLM/RAG/multimodal fundamentals
- Week 6: Triage API integration
- Week 7: MCP logistics tool stubs
- Week 8: Pins/versioning implementation
- Week 9: Security smoke testing and redaction
- Week 10: Catalog system implementation

## Success Metrics
- End-to-end system running from single command
- Comprehensive test coverage with green CI
- Documentation covering all required artifacts
- Peer review process completed
- Successful live demo with 10 API calls under $1.00